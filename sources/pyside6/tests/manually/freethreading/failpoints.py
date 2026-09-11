#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""Deterministic lifetime races, using the failpoints in libshiboken.

What each test is about, and what it does and does not prove, is in README.md
next to this file. The machinery is in fpharness.py.

    BUILD_DIR=<build> python failpoints.py
    BUILD_DIR=<build> python failpoints.py weakrefs

failpoint_matrix.py is the other way in: one subprocess per test, on the three
interpreters the validation plan names.
"""

from __future__ import annotations

import ctypes
import gc
import threading
import time
import weakref

import fpharness as fp
from fpharness import (FREE_THREADED, Failpoint, Shiboken, Test, counterproof,
                       gil_enabled, qml_create, qml_engine, qt_app,
                       run_threads)
from PySide6.QtCore import QByteArray, QObject, QRecursiveMutex


def test_weakrefs_while_deallocating() -> str:
    """B7-2: the deallocator clears weakrefs while another thread holds refs."""
    callbacks = []
    refs = {}
    ready = threading.Event()

    # The object is created in the worker: biased reference counting makes the
    # creating thread the owner, so a del elsewhere would not deallocate here.
    with Failpoint("dealloc-before-weakrefs") as point:
        def drop():
            obj = QObject()
            obj.setObjectName("victim")
            refs["plain"] = weakref.ref(obj)
            refs["cb"] = weakref.ref(obj, lambda r: callbacks.append(r))
            refs["proxy"] = weakref.proxy(obj)
            ready.set()
            del obj          # last strong reference, parks in the deallocator

        dropper = threading.Thread(target=drop)
        dropper.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never created the object"
        plain, with_callback, proxy = refs["plain"], refs["cb"], refs["proxy"]
        if not point.wait_until_reached():
            return "FAIL: deallocation never reached the failpoint"

        # Dying, but the weakrefs are not cleared yet: this is what raced.
        seen = [plain() is not None, with_callback() is not None]
        try:
            proxy.objectName()
            proxy_alive = True
        except ReferenceError:
            proxy_alive = False

        point.release()
        dropper.join(timeout=5)
        if dropper.is_alive():
            return "FAIL: the deallocating thread did not come back"

    if plain() is not None or with_callback() is not None:
        return "FAIL: a weakref survived the deallocation"
    if len(callbacks) != 1:
        return f"FAIL: callback ran {len(callbacks)} times, expected once"
    if callbacks[0]() is not None:
        return "FAIL: the callback saw a live referent"
    return f"ok (alive during dealloc: {seen}, proxy: {proxy_alive})"


def test_replacement_wrapper_while_dying() -> str:
    """B4-1: a lookup between unregistering and the C++ destructor."""
    state = {}
    ready = threading.Event()

    # In the worker, for the reason test_weakrefs_while_deallocating gives.
    # QRecursiveMutex and not QObject: a QObject's destroyed() signal
    # invalidates a stray wrapper afterwards and hides the window.
    def drop():
        obj = QRecursiveMutex()
        state["addr"] = Shiboken.getCppPointer(obj)[0]
        state["id"] = id(obj)
        ready.set()
        del obj

    with Failpoint("dealloc-before-destroy") as point:
        worker = threading.Thread(target=drop)
        worker.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never created the object"
        if not point.wait_until_reached():
            return "FAIL: deallocation never reached the failpoint"

        # The entry is gone, the C++ object is not destroyed yet. A lookup
        # here sees true absence, which is what has to stop being enough.
        replacement = Shiboken.wrapInstance(state["addr"], QRecursiveMutex)
        fresh = id(replacement) != state["id"]

        point.release()
        worker.join(timeout=5)
        if worker.is_alive():
            return "FAIL: the deallocating thread did not come back"

    if Shiboken.isValid(replacement):
        return ("FAIL: the replacement wrapper outlived the C++ object and is "
                f"still valid (a second wrapper was made: {fresh})")
    return "ok - no wrapper was published for a dying object"


def test_replacement_wrapper_before_cpp_dtor() -> str:
    """B4-1, the half the test above cannot see.

    `replacement-while-dying` parks before deallocData(), where the tombstone
    has just been set. The window that matters opens after it: deallocData()
    goes through the wrapper map on its way out, and until this test existed
    it took the tombstone with it - so between that point and the C++
    destructor a lookup saw true absence again, which is the very thing the
    tombstone was introduced to end.
    """
    state = {}
    ready = threading.Event()

    def drop():
        obj = QRecursiveMutex()
        state["addr"] = Shiboken.getCppPointer(obj)[0]
        state["id"] = id(obj)
        ready.set()
        del obj

    with Failpoint("dealloc-before-cpp-dtor") as point:
        worker = threading.Thread(target=drop)
        worker.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never created the object"
        if not point.wait_until_reached():
            return "FAIL: deallocation never reached the failpoint"

        # The wrapper is gone, the C++ object is not. Only the tombstone
        # stands between this lookup and a wrapper for a doomed address.
        replacement = Shiboken.wrapInstance(state["addr"], QRecursiveMutex)
        fresh = id(replacement) != state["id"]

        point.release()
        worker.join(timeout=5)
        if worker.is_alive():
            return "FAIL: the deallocating thread did not come back"

    if Shiboken.isValid(replacement):
        return ("FAIL: a wrapper was published after the wrapper was freed and "
                f"before the C++ destructor ran (second wrapper: {fresh})")
    return "ok - the tombstone holds until the destructor is past"


def test_replacement_wrapper_for_child_in_dealloc() -> str:
    """The child window again, reached through the deallocator this time.

    `replacement-of-owned-child` drives it with `Shiboken.delete()`, which
    goes through finishDestruction(). Dropping the last reference does not:
    the deallocator has its own copy of the same sequence, and it did not
    have the child tombstones - `deallocData()` releases the owned children
    and the parent's C++ destructor deletes them a step later, which is the
    same window one function further along.

    The failpoint parks in the child's own deallocation, which runs inside
    the parent's. Both are past their wrappers and neither C++ destructor has
    run, so the tombstone the parent laid for the child is all that stands
    between the lookup below and a doomed address.
    """
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    state = {}
    ready = threading.Event()

    def drop():
        parent = sample.ObjectType()
        child = sample.ObjectType.create()
        child.setParent(parent)
        state["addr"] = Shiboken.getCppPointer(child)[0]
        ready.set()
        del child          # the parent holds it, so this frees nothing
        del parent

    with Failpoint("dealloc-before-cpp-dtor") as point:
        worker = threading.Thread(target=drop)
        worker.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never built the pair"
        if not point.wait_until_reached():
            return "FAIL: deallocation never reached the failpoint"

        replacement = Shiboken.wrapInstance(state["addr"], sample.ObjectType)

        point.release()
        worker.join(timeout=5)
        if worker.is_alive():
            return "FAIL: the deallocating thread did not come back"

    if Shiboken.isValid(replacement):
        return "FAIL: a wrapper was published for a child the parent deletes"
    return "ok - the child's tombstone holds in the deallocator too"


def test_constructor_claim() -> str:
    """B5-3, the half `two-thread-ctor` cannot reach: claiming comes first.

    That test shows exactly one thread taking the slot. But the claim happens
    *after* the C++ constructor, so the loser has built its object anyway -
    and, for a QObject, hung it in Qt's tree - before it hears that it lost.

    The first thread parks where it is about to publish its pointer; by then
    it has built its object. The second runs the same base `__init__` right
    there, and the parent's children are counted while the first is still
    parked: released, it finds the slot taken and deletes what it built, and
    both outcomes look alike again.

    sample.ObjectType rather than a QObject because Qt refuses to parent
    across threads, so a QObject built on a worker never reaches the tree and
    the count cannot see the second object at all.

    What the A/B side actually reports is a crash, not this test's message:
    the loser's object is hung in the parent and then deleted by the
    constructor's own bail-out, so the parent is left with a dangling child
    and the process dies clearing the frame. The count below is the check
    that would speak if it got that far, and it is the reason the count is
    taken while the first thread is still parked.
    """
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    holder = sample.ObjectType()
    victim = sample.ObjectType.__new__(sample.ObjectType)
    errors = {}

    def initialize(which: str) -> None:
        try:
            sample.ObjectType.__init__(victim, holder)
        except RuntimeError as exc:
            errors[which] = str(exc)

    with Failpoint("ctor-before-publish") as point:
        winner = threading.Thread(target=initialize, args=("first",))
        winner.start()
        if not point.wait_until_reached():
            return "FAIL: the first constructor never reached the failpoint"

        loser = threading.Thread(target=initialize, args=("second",))
        loser.start()
        loser.join(timeout=5)
        if loser.is_alive():
            return "FAIL: the second constructor did not come back"

        children = len(holder.children())

        point.release()
        winner.join(timeout=5)
        if winner.is_alive():
            return "FAIL: the first constructor did not come back"

    if "second" not in errors:
        return f"FAIL: the second __init__ reported success ({children} children)"
    if children != 1:
        return f"FAIL: {children} C++ objects were built for one wrapper"
    return "ok - the second thread was refused before it built anything"


def test_replacement_wrapper_for_owned_child() -> str:
    """B4-1 one level down: the children a destructor takes with it.

    A tombstone covers the object being destroyed. It does not cover what the
    object owns: invalidate() hands the owned children back blank, their
    entries leave the map, and the parent's C++ destructor deletes them a line
    later. In between, a lookup on a child address sees true absence - the
    same defect the tombstone was introduced to end, only one level down.

    sample.ObjectType rather than a QObject on purpose: a QObject is the one
    type the tombstone makes an exception for, so it cannot show this.
    """
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    parent = sample.ObjectType()
    child = sample.ObjectType.create()
    child.setParent(parent)
    address = Shiboken.getCppPointer(child)[0]

    with Failpoint("delete-before-owned-dtor") as point:
        worker = threading.Thread(target=lambda: Shiboken.delete(parent))
        worker.start()
        if not point.wait_until_reached():
            return "FAIL: the deletion never reached the failpoint"

        # The child is blank and the destructor that frees it has not run.
        replacement = Shiboken.wrapInstance(address, sample.ObjectType)

        point.release()
        worker.join(timeout=5)
        if worker.is_alive():
            return "FAIL: the deleting thread did not come back"

    if Shiboken.isValid(replacement):
        return "FAIL: a wrapper was published for a child the parent deletes"
    return "ok - the child's tombstone holds until the parent's destructor is past"


def test_dying_qobject_argument() -> str:
    """The exception the tombstone makes for QObject, from both sides.

    A tombstone refuses to hand out a wrapper for an address that is being
    destroyed. `destroyed(QObject *)` is emitted from inside that very
    destruction and its argument is meant to be used, so the refusal does not
    apply to a type that invalidates such wrappers itself - which is what
    PySide does right after the signal. Both halves are the claim: usable in
    the handler, dead afterwards. If the second half ever stopped holding,
    the exception would be handing out a wrapper nobody ever invalidates,
    which is the defect the tombstone exists for.
    """
    seen = {}
    kept = []

    obj = QObject()
    obj.setObjectName("victim")

    def on_destroyed(argument):
        kept.append(argument)
        try:
            seen["name"] = argument.objectName()
        except RuntimeError as exc:
            seen["error"] = repr(exc)

    obj.destroyed.connect(on_destroyed)
    del obj
    gc.collect()

    if not kept:
        return "FAIL: destroyed() never ran"
    if "error" in seen:
        return f"FAIL: the argument was unusable inside the handler: {seen['error']}"
    if seen.get("name") != "victim":
        return f"FAIL: the argument was not the object: {seen.get('name')!r}"
    if Shiboken.isValid(kept[0]):
        return "FAIL: the wrapper handed to the handler is still valid afterwards"
    return "ok - usable in the handler, invalid once the signal is past"


def test_external_destruction_leaves_a_tombstone() -> str:
    """A destruction C++ started, from both ends.

    The deallocator and Shiboken.delete() run the C++ destructor themselves,
    so they know when it is past. This one does not: foreign C++ deletes an
    object Python knows, the generated wrapper destructor reports it through
    Object::destroy(), and nothing calls the binding again. Removing the map
    entry there leaves true absence for every base destructor still to come.

    Both halves are the claim, and the second is what keeps the first from
    being a leak: refused while the destruction runs, and free again once the
    memory has gone back - which the wrapper's operator delete is what says.
    """
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    ready = threading.Event()
    parent = sample.ObjectType()
    # Built from Python, so it is an ObjectTypeWrapper and its destructor
    # reports to the binding. ObjectType.create() hands out a plain C++
    # instance with no wrapper at all, and deleting one of those is a window
    # nothing can see - not this one.
    child = sample.ObjectType()
    child.setObjectName("victim")
    child.setParent(parent)
    address = Shiboken.getCppPointer(child)[0]
    del child                      # the parent holds it; nothing is destroyed

    with Failpoint("destroy-after-tombstone") as point:
        def kill():
            ready.set()
            parent.killChild("victim")   # plain C++ delete, parks in destroy()

        killer = threading.Thread(target=kill)
        killer.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never started"
        if not point.wait_until_reached():
            return "FAIL: the destruction never reached the failpoint"

        during = Shiboken.wrapInstance(address, sample.ObjectType)
        if Shiboken.isValid(during):
            return "FAIL: a valid wrapper was published while C++ destroyed the object"

        point.release()
        killer.join(timeout=5)
        if killer.is_alive():
            return "FAIL: the destroying thread did not come back"

    # The memory has gone back, so the address is nobody's identity any more
    # and the tombstone has to be gone with it. Still standing, it would
    # refuse this address for the rest of the process.
    after = Shiboken.wrapInstance(address, sample.ObjectType)
    if not Shiboken.isValid(after):
        return "FAIL: the tombstone outlived the memory it stood for"
    return "ok - refused while destroying, gone once the memory went back"


def test_stray_wrapper_outlives_the_tombstone() -> str:
    """The other end of the exception: what it let through, it takes back.

    The exception is asked per type, not per moment, so for a QObject the
    whole destruction is open, not just the destroyed() emit. A conversion
    that lands after the signal - here, past the C++ destructor and before
    the tombstone falls - used to get a wrapper that was registered in the
    map, said "valid", and pointed at freed memory. Nothing invalidated it:
    PySide's own path runs earlier, with the property data.

    Now such a wrapper stays out of the map and belongs to the tombstone,
    which invalidates it on the way out. Both halves are the claim: usable
    while the destruction runs, dead once it cannot reach the address.
    """
    shared = {}
    ready = threading.Event()

    with Failpoint("dealloc-before-retire") as point:
        # Created in the worker for the reason the weakref test gives: biased
        # reference counting makes the creating thread the owner.
        def drop():
            obj = QObject()
            obj.setObjectName("victim")
            shared["address"] = Shiboken.getCppPointer(obj)[0]
            ready.set()
            del obj          # last strong reference, parks past the destructor

        dropper = threading.Thread(target=drop)
        dropper.start()
        if not ready.wait(timeout=5):
            return "FAIL: the worker never created the object"
        if not point.wait_until_reached():
            return "FAIL: deallocation never reached the failpoint"

        stray = Shiboken.wrapInstance(shared["address"], QObject)
        if not Shiboken.isValid(stray):
            return "FAIL: the exception did not hand out a usable wrapper"

        point.release()
        dropper.join(timeout=5)
        if dropper.is_alive():
            return "FAIL: the deallocating thread did not come back"

    if Shiboken.isValid(stray):
        return "FAIL: the wrapper is still valid after the tombstone fell"
    return "ok - the tombstone invalidated what it let through"


def test_destroy_while_call_in_flight() -> str:
    """The lease window: destruction arriving while a call holds a lease.

    The method is bound *before* the failpoint is armed, and that is the
    whole test. `obj.objectName()` is two leases, not one: `tp_getattro`
    takes one to hand out the bound method, and the call takes another.
    Written as one expression the thread parks in the first of them, the
    destruction lands in the gap between the two, and the *second* lease is
    refused - correctly, because at that moment no call is in flight. That
    is what this test measured for days, and it is not what it claims.
    """
    obj = QObject()
    obj.setObjectName("leased")
    bound = obj.objectName
    result = {}

    with Failpoint("lease-after-acquire") as point:
        def call():
            try:
                result["name"] = bound()
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        caller = threading.Thread(target=call)
        caller.start()
        if not point.wait_until_reached():
            return "FAIL: the call never reached the failpoint"

        Shiboken.delete(obj)     # must be deferred, not run underneath

        point.release()
        caller.join(timeout=5)
        if caller.is_alive():
            return "FAIL: the calling thread did not come back"

    if "error" in result:
        return f"FAIL: the leased call raised {result['error']}"
    if result.get("name") != "leased":
        return f"FAIL: the leased call returned {result.get('name')!r}"
    return "ok"


def test_two_threads_one_constructor() -> str:
    """B5-3: two threads run the same base __init__ on one object."""
    class Sub(QObject):
        pass

    obj = Sub.__new__(Sub)
    results = []

    def initialize():
        try:
            QObject.__init__(obj)
            results.append("won")
        except RuntimeError as error:
            results.append(f"lost: {error}")

    # A Python subclass can hand self to another thread before it calls the
    # base initializer, which is how two of them arrive at the same slot.
    with Failpoint("ctor-before-publish") as point:
        first = threading.Thread(target=initialize)
        first.start()
        if not point.wait_until_reached():
            return "FAIL: the constructor never reached the failpoint"
        second = threading.Thread(target=initialize)
        second.start()
        second.join(timeout=5)
        point.release()
        first.join(timeout=5)
        if first.is_alive() or second.is_alive():
            return "FAIL: an initializing thread did not come back"

    winners = results.count("won")
    if winners != 1:
        return (f"FAIL: {winners} of {len(results)} threads claimed the slot; "
                "each of them constructed a C++ object")
    return "ok - one thread claimed the slot, the other was refused"


def test_no_raw_lock_while_python_runs() -> str:
    """FT8 invariant 2: no binding raw lock spans Python. A __del__ asks it."""
    seen = []

    class Watcher(QObject):
        def __del__(self):
            seen.append(Shiboken.heldRawLocks())

    for _ in range(50):
        watcher = Watcher()
        watcher.setObjectName("watched")
        child = QObject(watcher)          # a parent graph to tear down
        del child
        del watcher

    if not seen:
        return "FAIL: no __del__ ran, the test proves nothing"
    held = [s for s in seen if s not in ("", "none")]
    if held:
        return f"FAIL: Python ran with raw locks held: {sorted(set(held))}"
    return f"ok ({len(seen)} destructions, none under a lock)"


def test_lock_free_during_conversion() -> str:
    """The same invariant inside a generated entry point, via __index__."""
    data = QByteArray(b"abcdef")
    seen = []

    class Index:
        def __index__(self):
            seen.append((Shiboken.heldRawLocks(), Shiboken.activeCalls(data)))
            return 2

    for _ in range(100):
        data.at(Index())

    if not seen:
        return "FAIL: the conversion never asked for __index__"
    held = {locks for locks, _ in seen if locks not in ("", "none")}
    if held:
        return f"FAIL: a conversion ran Python with raw locks held: {sorted(held)}"
    if FREE_THREADED and not all(leases for _, leases in seen):
        return ("FAIL: the probe ran with no lease on the receiver, so it was "
                "not inside the call")
    return f"ok ({len(seen)} conversions, none under a lock)"


def test_state_lock_is_a_leaf() -> str:
    """FT8 invariant 7: transactions run past a parked guard holder."""
    anchor = QObject()
    anchor.setObjectName("anchor")
    outcome = {}

    with Failpoint("lease-after-acquire", timeout_ms=20000) as point:
        parker = threading.Thread(target=lambda: anchor.objectName())
        parker.start()
        if not point.wait_until_reached():
            return "FAIL: the call never reached the failpoint"

        def churn():
            for _ in range(200):
                parent = QObject()
                child = QObject(parent)
                child.setObjectName("c")
                child.setParent(None)
                Shiboken.delete(child)
                Shiboken.delete(parent)

        outcome["errors"] = run_threads(churn, timeout=20)

        point.release()
        parker.join(timeout=5)

    if outcome["errors"]:
        return f"FAIL: the transactions reported {outcome['errors']}"
    return "ok (200 graph transactions ran past a parked guard holder)"


def test_no_leaked_lease() -> str:
    """Invariants 9 and 10: six shapes of exit, none leaves a lease open."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL has no leases"

    obj = QObject()
    obj.setObjectName("subject")
    other = QObject()
    left = []

    def check(what: str) -> None:
        for probe in (obj, other):
            if count := Shiboken.activeCalls(probe):
                left.append(f"{what}: {count}")

    obj.objectName()
    check("method")
    obj.objectName
    check("attribute")
    _ = obj == other
    check("comparison")
    try:
        obj.setObjectName(object())          # no overload takes that
    except TypeError:
        pass
    check("conversion failure")

    class Raiser(QObject):
        def childEvent(self, event):
            raise RuntimeError("from an override")

    child = QObject()
    try:
        child.setParent(Raiser())            # C++ calls back into Python
    except RuntimeError:
        pass
    if count := Shiboken.activeCalls(child):
        left.append(f"exception from an override: {count}")

    mutex = QRecursiveMutex()                # lock() is allow-thread
    mutex.lock()
    mutex.unlock()
    if count := Shiboken.activeCalls(mutex):
        left.append(f"allow-thread detach: {count}")

    if left:
        return f"FAIL: leases left open -> {left}"
    return "ok (six exit shapes, no lease left open)"


def _guard_against_lock(acquire, release) -> bool:
    """Two threads in opposite order: guard-then-lock against lock-then-guard.

    ChildAdded is delivered through the application, so childEvent() is not
    called without one - and the override is the whole point here.
    """
    qt_app()
    child = QObject()
    child.setObjectName("subject")
    ready = threading.Event()
    entered = threading.Event()
    finished = []

    class Parent(QObject):
        def childEvent(self, event):
            entered.set()
            ready.wait(5)
            acquire()                # the guard on child is held right now
            release()

    parent = Parent()

    def take_guard_then_lock():
        child.setParent(parent)      # guard(child) -> childEvent -> acquire()
        finished.append("guard-first")

    def take_lock_then_guard():
        acquire()
        ready.set()
        try:
            child.objectName()       # wants guard(child)
        finally:
            release()
        finished.append("lock-first")

    first = threading.Thread(target=take_guard_then_lock)
    first.start()
    if not entered.wait(5):
        raise RuntimeError("the override never ran")
    second = threading.Thread(target=take_lock_then_guard)
    second.start()
    first.join(timeout=10)
    second.join(timeout=10)
    return len(finished) == 2


def test_guard_against_python_lock() -> str:
    """A Python lock resolves the inversion, because waiting for it detaches."""
    lock = threading.Lock()
    if not _guard_against_lock(lock.acquire, lock.release):
        return "FAIL: threading.Lock deadlocked against the receiver guard"
    return "ok (both orders came back)"


def test_guard_against_annotated_lock() -> str:
    """The same with a Qt lock whose lock() carries allow-thread."""
    mutex = QRecursiveMutex()
    if not _guard_against_lock(mutex.lock, mutex.unlock):
        return "FAIL: an annotated Qt lock deadlocked against the guard"
    return "ok (both orders came back)"


def test_guard_spans_a_native_wait() -> str:
    """The documented boundary, measured instead of deadlocked."""
    if gil_enabled():
        return "skipped: the GIL makes this measurement meaningless"
    qt_app()

    libc = ctypes.PyDLL(None)
    child = QObject()
    child.setObjectName("subject")
    state = {"inside": False, "native": True}

    class Parent(QObject):
        def childEvent(self, event):
            state["inside"] = True
            if state["native"]:
                libc.usleep(ctypes.c_uint(1500000))
            else:
                time.sleep(1.5)         # detaches, so the guard is suspended

    def measure(native: bool) -> float:
        state["inside"] = False
        state["native"] = native
        parent = Parent()
        holder = threading.Thread(target=lambda: child.setParent(parent),
                                  daemon=True)
        holder.start()
        deadline = time.monotonic() + 5
        while not state["inside"] and time.monotonic() < deadline:
            time.sleep(0.005)
        if not state["inside"]:
            raise RuntimeError("the override never ran")
        started = time.monotonic()
        child.objectName()
        waited = time.monotonic() - started
        holder.join(timeout=5)
        child.setParent(None)
        return waited

    with_native = measure(native=True)
    with_python = measure(native=False)

    if with_native < 1.0:
        return (f"FAIL: a native attached wait no longer holds the guard "
                f"({with_native:.2f}s) - the boundary policy needs updating")
    if with_python > 1.0:
        return (f"FAIL: a detaching wait held the guard for {with_python:.2f}s; "
                f"the guard must be suspended there")
    return (f"ok (native wait holds the guard {with_native:.2f}s, "
            f"a detaching one {with_python:.2f}s)")


def test_qml_placement_nests() -> str:
    """B15-4: a QObject built inside __init__ must not take QML's address."""
    if not fp.QML_READY:
        return "skipped: QtQml not available"
    engine = qml_engine()
    fp.inner_names.clear()
    obj, error = qml_create(engine, "Placed { }")
    if obj is None:
        return f"FAIL: QML did not construct the element: {error}"
    if obj.objectName() != "placed":
        return f"FAIL: the placed object lost its identity: {obj.objectName()!r}"
    if not fp.inner_names:
        return "FAIL: the nested construction never ran"
    return f"ok (QML placement, {len(fp.inner_names)} nested constructions)"


def test_qml_placement_in_parallel() -> str:
    """Two threads inside QML construction at the same time, by construction."""
    if not fp.QML_READY:
        return "skipped: QtQml not available"
    qt_app()
    results: list[str] = []
    fp.parallel_barrier = threading.Barrier(2, timeout=15)

    def build():
        obj, error = qml_create(qml_engine(), "Parallel { }")
        if obj is None:
            raise RuntimeError(f"no object: {error}")
        results.append(obj.objectName())

    try:
        errors = run_threads(build, count=2, timeout=30)
    finally:
        fp.parallel_barrier = None
    if errors:
        return f"FAIL: {errors}"
    if len(results) != 2 or any(name != "parallel" for name in results):
        return f"FAIL: {results}"
    return "ok (two threads inside QML construction at once)"


def test_qml_placement_unwinds() -> str:
    """A guard, not a proof: the error path leaves nothing staged."""
    if not fp.QML_READY:
        return "skipped: QtQml not available"
    engine = qml_engine()
    for _ in range(10):
        qml_create(engine, "Failing { }")

    survivor, error = qml_create(engine, "Placed { }")
    if survivor is None:
        return f"FAIL: no construction after the errors: {error}"
    if survivor.objectName() != "placed":
        return "FAIL: a construction after the errors lost its identity"
    return "ok (10 failed QML constructions, the next one is intact)"


def test_native_preflight() -> str:
    """An unattached thread does address checks only, never type state."""
    from PySide6.QtCore import QRunnable, QThreadPool
    qt_app()

    ran = threading.Event()

    class Work(QRunnable):
        def run(self):              # a virtual, called from a pool thread
            ran.set()

    pool = QThreadPool.globalInstance()
    for _ in range(50):
        ran.clear()
        work = Work()
        work.setAutoDelete(False)
        pool.start(work)
        if not ran.wait(timeout=10):
            return "FAIL: the override never ran on a pool thread"
    pool.waitForDone(10000)
    return "ok (50 virtuals entered from threads with no thread state)"


def test_hierarchy_snapshot() -> str:
    """A module publishes edges while a traversal holds an iterator.

    A guard, not a proof - see README.md. It makes the race deterministic,
    which is what a sanitizer needs, but it cannot fail on its own.
    """
    import importlib
    import tempfile
    qt_app()

    # Each import runs the module's generated initInheritance(), which adds
    # one edge per class - enough insertions to grow the map the traversal
    # below is standing in the middle of. Module init is the only thing that
    # adds edges at all, so without at least one import that goes through,
    # this test watches an idle map and reports success either way.
    #
    # The shiboken test modules are in the list because a build that is not a
    # full one has no other PySide6 modules to import - a Core subset with
    # --build-tests, which is what the sanitizer trees are, would otherwise
    # find nothing here.
    modules = ["PySide6.QtGui", "PySide6.QtNetwork", "PySide6.QtXml",
               "PySide6.QtSql", "PySide6.QtSvg", "PySide6.QtTest",
               "PySide6.QtWidgets", "PySide6.QtPrintSupport",
               "PySide6.QtOpenGL", "PySide6.QtUiTools",
               "sample", "other", "minimal", "smart"]
    outcome = {}
    imported = []

    with tempfile.NamedTemporaryFile(suffix=".dot") as out:
        with Failpoint("hierarchy-mid-traversal", timeout_ms=30000) as point:
            def traverse():
                outcome["written"] = Shiboken.dumpTypeGraph(out.name)

            reader = threading.Thread(target=traverse)
            reader.start()
            if not point.wait_until_reached():
                return "FAIL: the traversal never reached the failpoint"

            for name in modules:
                try:
                    importlib.import_module(name)
                    imported.append(name)
                except ImportError:
                    pass

            point.release()
            reader.join(timeout=30)
            if reader.is_alive():
                return "FAIL: the traversal did not come back"

    if not imported:
        return ("FAIL: no module could be imported, so no edge was ever added "
                "and the traversal raced nothing")
    if not outcome.get("written"):
        return "FAIL: the traversal did not finish its file"
    return ("ok (a traversal survived the init of "
            f"{', '.join(imported)} under it)")


def test_type_mutation_during_destruction() -> str:
    """FT8 validation row "state lock": __bases__ swaps race destruction."""
    class Mutable(QObject):
        pass

    class Other(QObject):
        pass

    stop = threading.Event()

    def destroyer():
        while not stop.is_set():
            for obj in [Mutable() for _ in range(20)]:
                Shiboken.delete(obj)

    def mutator():
        try:
            for _ in range(200):
                Mutable.__bases__ = (Other,)
                Mutable.__bases__ = (QObject,)
        finally:
            stop.set()

    if errors := run_threads([destroyer, mutator], timeout=30):
        return f"FAIL: {errors}"
    return "ok (200 bases swaps raced against destruction, no failure)"


# The lock pairs the inventory in doc/developer/freethreading.md names. All
# of them have the lazy-type lock on the outside, which is why it ranks
# lowest.
KNOWN_NESTINGS = {"lazy type -> wrapper map", "lazy type -> state",
                  "lazy type -> class hierarchy"}


def test_lock_order() -> str:
    """FT8 invariant 1: only the nestings the inventory knows ever happen."""
    from PySide6.QtCore import Signal, Slot
    qt_app()

    class Emitter(QObject):
        fired = Signal(int)
        named = Signal(str)

        @Slot(int)
        def on_fired(self, value):
            self.setProperty("last", value)

    def churn():
        for i in range(150):
            emitter = Emitter()
            child = QObject(emitter)
            emitter.fired.connect(emitter.on_fired)
            emitter.named.connect(lambda text: None)
            emitter.fired.emit(i)
            emitter.named.emit(str(i))
            emitter.setProperty("items", [QObject(), QObject()])
            emitter.fired.disconnect(emitter.on_fired)
            child.setParent(None)
            Shiboken.delete(child)
            Shiboken.delete(emitter)

    if errors := run_threads(churn, count=4, timeout=60):
        return f"FAIL: {errors}"

    nestings = Shiboken.lockNestings()
    if not nestings:
        return "ok (no two binding locks were ever held at once)"
    lines = nestings.split("\n")
    if unknown := [line for line in lines if line not in KNOWN_NESTINGS]:
        return f"FAIL: nesting(s) the inventory does not know: {'; '.join(unknown)}"
    return f"ok ({len(lines)} known nesting(s): {'; '.join(lines)})"


def test_lazy_lock_spans_destruction() -> str:
    """Open, owned by the lazy protocol: B13-5 from the destruction end."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL takes no lazy-type lock"

    test_no_raw_lock_while_python_runs()
    test_no_leaked_lease()

    # Only the lazy line: the wrapper-map exception is a different, documented
    # one, taken on every type-narrowed lookup.
    taken = [line for line in Shiboken.contractExceptions().split("\n")
             if line.startswith("lazy type")]
    if not taken:
        return "ok - no raw lock is held where the contract forbids one"
    return f"FAIL: the contract's exception was taken -> {'; '.join(taken)}"


def test_metaobject_lifetime() -> str:
    """Open, and NOT free-threading: a shared wrapper invalidated by a
    stranger's destruction.

    Every QObject answers metaObject() with the same &QObject::staticMetaObject,
    so the map holds exactly one wrapper for it and every instance hands out
    that one. Destroying any single QObject invalidates it, and every other
    holder is hit. The C++ object behind it is static and never dies; the
    invalidation is a guess PySide makes because it does not know when the
    referent dies.

    That is reproducible with a GIL, in four lines and without threads:

        a, b = QObject(), QObject()
        ma = a.metaObject()
        Shiboken.delete(b)          # a stranger
        ma.className()              # RuntimeError: already deleted

    Bisected to 4c1d56fb6 (29.07.2026), which moved the bookkeeping in
    callCppDestructors() ahead of the C++ destructors - before that,
    clearReferences() had taken the referred objects out before invalidate()
    ran. The move is right and free-threading-only in its reason, but it sits
    in common code, so a GIL build gets the side effect and none of the
    benefit. The fix belongs on the free-threading branch, not in this series.
    """
    if not FREE_THREADED or gil_enabled():
        return "skipped: the race needs the GIL off"
    qt_app()

    def churn():
        for _ in range(150):
            obj = QObject()
            obj.metaObject().className()
            Shiboken.delete(obj)

    if errors := run_threads(churn, count=4, timeout=60):
        return f"FAIL: {len(errors)} of 600 calls lost the wrapper: {errors[0]}"
    return "ok - the returned metaObject wrapper now survives its use"


TESTS = {
    "weakrefs": Test(test_weakrefs_while_deallocating),
    # Was an expected FAIL on a wrong explanation; see the docstring.
    "lease-vs-destroy": Test(test_destroy_while_call_in_flight),
    "replacement-while-dying": Test(test_replacement_wrapper_while_dying),
    "two-thread-ctor": Test(test_two_threads_one_constructor),
    # Asked with the reservation off: ConstructorClaim now refuses the second
    # thread before it ever reaches the transaction, so with everything on
    # there is nothing left for this one to see.
    "proof-ctor-commit": Test(lambda: counterproof("ConstructorCommit",
                                                   "two-thread-ctor",
                                                   context="ConstructorClaim")),
    "replacement-before-cpp-dtor": Test(test_replacement_wrapper_before_cpp_dtor),
    "dying-qobject-argument": Test(test_dying_qobject_argument),
    "proof-tombstones": Test(lambda: counterproof("Tombstones",
                                                  "replacement-while-dying")),
    "proof-tombstones-late": Test(lambda: counterproof(
        "Tombstones", "replacement-before-cpp-dtor")),
    "replacement-of-owned-child": Test(test_replacement_wrapper_for_owned_child),
    "replacement-of-child-in-dealloc":
        Test(test_replacement_wrapper_for_child_in_dealloc),
    "proof-tombstones-dealloc-children": Test(lambda: counterproof(
        "Tombstones", "replacement-of-child-in-dealloc")),
    "constructor-claim": Test(test_constructor_claim),
    "proof-constructor-claim": Test(lambda: counterproof(
        "ConstructorClaim", "constructor-claim")),
    "proof-tombstones-children": Test(lambda: counterproof(
        "Tombstones", "replacement-of-owned-child")),
    # The exception the tombstone makes for QObject is a measure like any
    # other: without the bit the tombstone refuses every dying identity, and
    # the destroyed() handler is handed a wrapper it cannot use.
    "proof-dying-qobject": Test(lambda: counterproof(
        "DyingConversionException", "dying-qobject-argument")),
    "external-destruction": Test(test_external_destruction_leaves_a_tombstone),
    # Without the bit Object::destroy() removes the entry as it always did,
    # and the stretch from there to the last base destructor is open.
    "proof-external-tombstones": Test(lambda: counterproof(
        "ExternalTombstones", "external-destruction")),
    "stray-outlives-tombstone": Test(test_stray_wrapper_outlives_the_tombstone),
    # Without the bit the wrapper the exception let through is registered as
    # any other, and the second half of the claim - dead once the destruction
    # is past - has nobody left to keep it.
    "proof-dying-strays": Test(lambda: counterproof(
        "DyingStrays", "stray-outlives-tombstone")),
    "no-lock-in-python": Test(test_no_raw_lock_while_python_runs),
    "no-lock-in-conversion": Test(test_lock_free_during_conversion),
    "state-lock-leaf": Test(test_state_lock_is_a_leaf),
    "no-leaked-lease": Test(test_no_leaked_lease),
    "guard-vs-python-lock": Test(test_guard_against_python_lock),
    "guard-vs-annotated-lock": Test(test_guard_against_annotated_lock),
    "guard-spans-native-wait": Test(test_guard_spans_a_native_wait),
    "qml-placement": Test(test_qml_placement_nests),
    "qml-placement-parallel": Test(test_qml_placement_in_parallel),
    "qml-placement-unwinds": Test(test_qml_placement_unwinds),
    "native-preflight": Test(test_native_preflight),
    "hierarchy-snapshot": Test(test_hierarchy_snapshot),
    "type-mutation": Test(test_type_mutation_during_destruction),
    "lock-order": Test(test_lock_order),
    # The two above have to fail once their measure is taken away, or they are
    # not testing it. Nothing else here can be asked that way: the remaining
    # measures are assertions, which abort rather than fail, or they are
    # invariants no switch can remove.
    "proof-qml-type": Test(lambda: counterproof("QmlPlacementType",
                                                "qml-placement")),
    "proof-qml-scope": Test(lambda: counterproof("QmlPlacementFree",
                                                 "qml-placement-parallel")),
    "proof-native-preflight": Test(lambda: counterproof("NativePreflight",
                                                        "native-preflight")),
    # Known open, and not free-threading: the same defect is four lines with
    # a GIL, see the docstring. Kept because this is where it was found.
    "metaobject-lifetime": Test(test_metaobject_lifetime, "FAIL"),
    # Known open, owned by the lazy protocol's replacement: the lazy-type lock
    # spans type creation, and a deferred destructor runs under it.
    "lazy-lock-spans-destruction": Test(test_lazy_lock_spans_destruction, "FAIL"),
}


if __name__ == "__main__":
    import sys
    sys.exit(fp.main(TESTS))
