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
import os
import subprocess
import sys
import threading
import time
import tracemalloc
import weakref

import fpharness as fp
from fpharness import (FREE_THREADED, Failpoint, FailpointThrow, Shiboken,
                       Test, counterproof, gil_enabled, qml_create, qml_engine,
                       qt_app, run_threads)
from PySide6.QtCore import (QByteArray, QObject, QRecursiveMutex, SIGNAL,
                            Qt, Signal, SLOT)


def test_signal_instance_leaves_its_type_collectable() -> str:
    """A class that keeps a bound signal of its own. See README."""
    def build():
        class Holder(QObject):
            fired = Signal()

        holder = Holder()
        # Class -> bound signal -> remembered type -> class. Only the last
        # edge is the record's, and the collector cannot see it.
        Holder.saved = holder.fired
        del holder
        return weakref.ref(Holder)

    ref = build()
    gc.collect()
    if ref() is not None:
        return "FAIL: the class survived a collection"
    return "ok"


_capsule_types = {}


def _capsule_classes():
    """One RepFile: Qt refuses a second class of the same name."""
    if "rep" in _capsule_types:
        return _capsule_types["rep"]
    try:
        from PySide6.QtRemoteObjects import RepFile
    except ImportError:
        return None
    rep = RepFile("""
POD Point{int x, int y}
class Simple
{
    PROP(int i = 2);
    PROP(float f = -1. READWRITE);
    PROP(QString text READWRITE);
    SLOT(void reset());
};
""")
    _capsule_types["rep"] = (rep.source["Simple"], rep.replica["Simple"],
                             rep.pod["Point"])
    return _capsule_types["rep"]


def test_capsule_method_owns_its_instance() -> str:
    """G80: a bound capsule method outlives its object. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL keeps the borrowed instance"
    classes = _capsule_classes()
    if classes is None:
        return "skipped: QtRemoteObjects is not in this build"
    Source = classes[0]

    source = Source()
    ref = weakref.ref(source)
    method = source.reset
    del source
    gc.collect()
    if ref() is None:
        return "FAIL: the object died under its bound method"
    try:
        method()
    except NotImplementedError:
        pass
    del method
    gc.collect()
    if ref() is not None:
        return "FAIL: the object outlived its bound method"

    # Instance -> dict -> bound method -> instance: the last edge must be
    # one the collector can see.
    source = Source()
    ref = weakref.ref(source)
    source.saved = source.reset
    del source
    gc.collect()
    if ref() is not None:
        return "FAIL: a method kept in the instance dict was not collected"

    # Whatever holds the instance must not be writable from Python.
    source = Source()
    ref = weakref.ref(source)
    method = source.reset
    try:
        method.__module__ = None
    except AttributeError:
        pass
    del source
    gc.collect()
    if ref() is None:
        return "FAIL: the method let go of its object through __module__"
    return "ok"


def test_capsule_access_does_not_leak() -> str:
    """G80: every access to a capsule method or property. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL keeps the old payload"
    classes = _capsule_classes()
    if classes is None:
        return "skipped: QtRemoteObjects is not in this build"
    Source, Replica, Point = classes
    source, replica, point = Source(), Replica(), Point(1, 2)
    accesses = {
        "method": lambda: replica.reset,
        "getter": lambda: replica.i,
        "setter": lambda: setattr(source, "f", 1.5),
        "pod getter": lambda: point.y,
    }
    source.f = 1.5
    if (replica.i, source.f, point.y) != (2, 1.5, 2):
        return "FAIL: a handler read the wrong instance or arguments"
    count = 10000
    for name, access in accesses.items():
        access()
        gc.collect()
        tracemalloc.start()
        before = tracemalloc.get_traced_memory()[0]
        for _ in range(count):
            access()
        gc.collect()
        grown = tracemalloc.get_traced_memory()[0] - before
        tracemalloc.stop()
        if grown > 50000:
            return f"FAIL: {name} kept {grown} bytes over {count} accesses"
    return "ok"


def test_source_property_read_as_copy() -> str:
    """G84: a source property read while another thread sets it. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL has no such race"
    classes = _capsule_classes()
    if classes is None:
        return "skipped: QtRemoteObjects is not in this build"
    source = classes[0]()
    source.text = "before"     # the instance's list no longer shares the type's
    result = {}
    with Failpoint("source-property-after-read") as point:
        reader = threading.Thread(target=lambda: result.update(text=source.text))
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the getter never reached the failpoint"
        source.text = "after"
        point.release()
        reader.join(timeout=10)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"
    if result.get("text") != "before":
        return f"FAIL: the getter returned {result.get('text')!r}, set after its read"
    if source.text != "after":
        return "FAIL: the setter was lost"
    return "ok"


def test_source_without_property_list() -> str:
    """G85: a source whose property list is gone. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL keeps the old code"
    # A regression crashes, so the scenario runs in a process of its own.
    if os.environ.get("FAILPOINT_PROPERTY_LIST_CHILD") != "1":
        env = dict(os.environ, FAILPOINT_PROPERTY_LIST_CHILD="1")
        proc = subprocess.run([sys.executable, __file__, "source-property-missing"],
                              env=env, capture_output=True, text=True,
                              timeout=fp.CHILD_TIMEOUT)
        if proc.returncode == 0:
            return "ok"
        return fp._reason(proc.stdout + proc.stderr) or f"FAIL: rc {proc.returncode}"

    classes = _capsule_classes()
    if classes is None:
        return "skipped: QtRemoteObjects is not in this build"
    for replacement in (None, 42):
        source = classes[0]()
        if replacement is None:
            del source.__PROPERTIES__
        else:
            source.__PROPERTIES__ = replacement
        for access in (lambda: source.text, lambda: setattr(source, "text", "x")):
            try:
                access()
            except RuntimeError:
                continue
            return f"FAIL: no error with __PROPERTIES__ = {replacement!r}"
    return "ok"


def test_metaclass_tuples_are_checked() -> str:
    """A3: a metaclass answers __mro__ and __bases__ with nonsense. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL reads the type's own slots"
    # A regression crashes, so the scenario runs in a process of its own.
    if os.environ.get("FAILPOINT_METACLASS_TUPLE_CHILD") != "1":
        env = dict(os.environ, FAILPOINT_METACLASS_TUPLE_CHILD="1")
        proc = subprocess.run([sys.executable, __file__, "metaclass-tuples"],
                              env=env, capture_output=True, text=True,
                              timeout=fp.CHILD_TIMEOUT)
        if proc.returncode == 0:
            return "ok"
        return fp._reason(proc.stdout + proc.stderr) or f"FAIL: rc {proc.returncode}"

    from PySide6.QtCore import Property
    qt_app()

    class BadMro(type(QObject)):
        @property
        def __mro__(cls):
            return (cls, 1, object)

    class Walked(QObject, metaclass=BadMro):
        pass

    class SelfBase(type(QObject)):
        @property
        def __bases__(cls):
            return (cls,)

    class Holder(QObject):
        @Property(int)
        def val(self):
            return 7

    # val is Holder's: the lookup for it recurses over Looped's __bases__.
    class Looped(Holder, metaclass=SelfBase):
        pass

    _KEEP_ALIVE.extend((Walked, Looped))
    for ask in (lambda: Walked.tr("text"), lambda: Looped().property("val")):
        try:
            ask()
        except TypeError:
            pass
    return "ok"


def test_signal_homonym_owned() -> str:
    """A4: the method a signal call found is replaced before it is bound. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL keeps the borrowed lookup"
    # A regression reads a freed function, so this runs on its own.
    if os.environ.get("FAILPOINT_HOMONYM_CHILD") != "1":
        env = dict(os.environ, FAILPOINT_HOMONYM_CHILD="1")
        proc = subprocess.run([sys.executable, __file__, "signal-homonym"],
                              env=env, capture_output=True, text=True,
                              timeout=fp.CHILD_TIMEOUT)
        if proc.returncode == 0:
            return "ok"
        return fp._reason(proc.stdout + proc.stderr) or f"FAIL: rc {proc.returncode}"

    qt_app()

    def make_ping():
        def ping(self):
            return "base"
        return ping

    # Built at runtime, so the class dict holds its only reference.
    Base = type("Base", (QObject,), {"ping": make_ping()})
    Sub = type("Sub", (Base,), {"ping": Signal()})
    obj = Sub()
    answer = []

    def call():
        try:
            answer.append(obj.ping())
        except BaseException as exc:      # noqa: BLE001
            answer.append(repr(exc))

    with Failpoint("signal-homonym-before-bind") as point:
        caller = threading.Thread(target=call)
        caller.start()
        if not point.wait_until_reached():
            return "FAIL: the signal call never reached the failpoint"
        Base.ping = lambda self: "replacement"
        gc.collect()
        # Functions of the same size: freed memory is reused by the next one.
        ballast = [(lambda self: "ballast") for _ in range(20000)]  # noqa: F841
        point.release()
        caller.join(timeout=10)
        if caller.is_alive():
            return "FAIL: the calling thread did not come back"
    if answer != ["base"]:
        return f"FAIL: the call answered {answer}, not the method it found"
    return "ok"


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


def test_teardown_waits_for_a_call_in_flight() -> str:
    """Application teardown against an open call. See README."""
    # Deleting the application ends it for every later test, so the scenario
    # runs in a process of its own.
    if os.environ.get("FAILPOINT_TEARDOWN_CHILD") != "1":
        env = dict(os.environ, FAILPOINT_TEARDOWN_CHILD="1")
        proc = subprocess.run([sys.executable, __file__, "teardown-vs-call"],
                              env=env, capture_output=True, text=True,
                              timeout=fp.CHILD_TIMEOUT)
        if proc.returncode == 0:
            return "ok"
        return fp._reason(proc.stdout + proc.stderr) or f"FAIL: rc {proc.returncode}"

    app = qt_app()
    obj = QObject()                       # Python owns it: teardown deletes it
    obj.setObjectName("leased")
    bound = obj.objectName
    destroyed = []
    # Direct: the deferred destructor runs where the last lease is released,
    # and there is no event loop to deliver a queued call.
    obj.destroyed.connect(lambda: destroyed.append(True), Qt.DirectConnection)
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

        Shiboken.delete(app)                  # destroyQCoreApplication()
        early = bool(destroyed)

        point.release()
        caller.join(timeout=5)
        if caller.is_alive():
            return "FAIL: the calling thread did not come back"

    if early:
        return "FAIL: teardown destroyed the object under a running call"
    if "error" in result:
        return f"FAIL: the leased call raised {result['error']}"
    if result.get("name") != "leased":
        return f"FAIL: the leased call returned {result.get('name')!r}"
    for _ in range(100):                      # a deferral may be queued
        if destroyed:
            return "ok"
        time.sleep(0.01)
    return "FAIL: the deferred destruction never ran"


def test_deferred_widget_destruction_in_main_thread() -> str:
    """A deferred destruction of a type that asks for the main thread."""
    # A QApplication, and one that is deleted at the end: a process of its
    # own, as for teardown-vs-call.
    if os.environ.get("FAILPOINT_WIDGET_CHILD") != "1":
        try:
            import PySide6.QtWidgets  # noqa: F401
        except ImportError:
            return "skipped: QtWidgets is not in this build"
        env = dict(os.environ, FAILPOINT_WIDGET_CHILD="1",
                   QT_QPA_PLATFORM="offscreen")
        proc = subprocess.run([sys.executable, __file__, "deferred-widget-dtor"],
                              env=env, capture_output=True, text=True,
                              timeout=fp.CHILD_TIMEOUT)
        if proc.returncode == 0:
            return "ok"
        return fp._reason(proc.stdout + proc.stderr) or f"FAIL: rc {proc.returncode}"

    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])                # noqa: F841
    widget = QWidget()
    widget.setObjectName("leased")
    bound = widget.objectName
    threads = []
    widget.destroyed.connect(lambda: threads.append(threading.current_thread()),
                             Qt.DirectConnection)
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
        Shiboken.delete(widget)               # deferred behind the lease
        point.release()
        caller.join(timeout=5)
        if caller.is_alive():
            return "FAIL: the calling thread did not come back"

    for _ in range(100):                      # the main thread's queue
        if threads:
            break
        time.sleep(0.01)
    if "error" in result:
        return f"FAIL: the leased call raised {result['error']}"
    if not threads:
        return "FAIL: the deferred destruction never ran"
    if threads[0] is not threading.main_thread():
        return f"FAIL: the widget was destroyed on {threads[0].name}"
    return "ok"


class _DictHolder(QObject):
    """A Python subclass: its tp_clear is CPython's subtype_clear."""


def _dict_first_access(obj) -> str:
    seen = {}
    with Failpoint("dict-before-publish") as point:
        def read():
            seen["dict"] = obj.__dict__

        reader = threading.Thread(target=read)
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the first access never reached the failpoint"
        # CPython creates the dict for a generic setattr, under the
        # object's critical section, while the reader waits.
        obj.marker = 1
        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"
    if seen["dict"] is not obj.__dict__:
        return "FAIL: the object got two dicts, one of them lost"
    if "marker" not in obj.__dict__:
        return "FAIL: the attribute set meanwhile is gone"
    return "ok"


class _DictValue(QByteArray):
    """A wrapper without signals, whose dict is made on first access."""


def test_dict_first_access() -> str:
    """Two first accesses to the instance dict. See README."""
    # Not a QObject: its constructor creates the dict before the object is
    # published, so there is no first access to race.
    for make in (QByteArray, _DictValue):
        result = _dict_first_access(make())
        if result != "ok":
            return f"{result} ({make.__name__})"
    return "ok"


def _dict_survives_clear(make) -> str:
    gc.collect()
    obj = make()
    obj.cycle = obj                          # only the collector frees it
    address = Shiboken.getCppPointer(obj)[0]
    del obj
    held = {}
    with Failpoint("clear-before-dict") as point:
        collector = threading.Thread(target=gc.collect)
        collector.start()
        if not point.wait_until_reached():
            return "FAIL: tp_clear never reached the failpoint"
        # The world runs again: the map hands out the wrapper tp_clear is on.
        wrapper = Shiboken.wrapInstance(address, QObject)
        held["dict"] = wrapper.__dict__
        point.release()
        collector.join(timeout=10)
        if collector.is_alive():
            return "FAIL: the collecting thread did not come back"
    if held["dict"] is not wrapper.__dict__:
        return "FAIL: tp_clear replaced the dict a reader holds"
    if held["dict"]:
        return "FAIL: tp_clear left the dict's contents"
    wrapper.__dict__.clear()
    return "ok"


def test_dict_survives_clear() -> str:
    """tp_clear against a reader of the instance dict. See README."""
    for make in (QObject, _DictHolder):
        result = _dict_survives_clear(make)
        if result != "ok":
            return f"{result} ({make.__name__})"
    return "ok"


def test_multiple_inheritance_pointer() -> str:
    """The lease's multiple-inheritance pointer arithmetic. See README."""
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    obj = sample.MDerived1()

    # Converted as a Base2: dynamic_cast finds MDerived1 again only if the
    # pointer it was handed really is the Base2 subobject of this object.
    if sample.MDerived1.transformFromBase2(obj) is not obj:
        return "FAIL: converted as Base2, C++ did not find the same object"
    if sample.MDerived1.transformFromBase1(obj) is not obj:
        return "FAIL: converted as Base1, C++ did not find the same object"

    # Received as a base: each base's own member, not the other's.
    for owner, method, want in ((sample.Base1, "base1Method", 1),
                                (sample.Base2, "base2Method", 2)):
        got = getattr(owner, method)(obj)
        if got != want:
            return (f"FAIL: {owner.__name__}.{method}() on an MDerived1 "
                    f"answered {got}, not {want}")

    # And the derived override still wins where it should.
    if obj.base2Method() != 20:
        return f"FAIL: the override answered {obj.base2Method()}, not 20"
    return "ok"


def test_lease_carries_the_pointer_it_validated() -> str:
    """B5-1: C++ deletes the object while a lease is out. See README."""
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    parent = sample.ObjectType()
    # Built from Python, so its destructor reports through Object::destroy().
    child = sample.ObjectType()
    child.setObjectName("leased")
    child.setParent(parent)
    address = Shiboken.getCppPointer(child)[0]
    result = {}

    with Failpoint("lease-after-acquire") as point:
        def read():
            try:
                result["address"] = int(Shiboken.VoidPtr(child))
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        reader = threading.Thread(target=read)
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the read never reached the failpoint"

        # An armed point stops one thread; this call passes it.
        parent.killChild("leased")

        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"

    if "error" in result:
        return f"FAIL: the leased read raised {result['error']}"
    got = result.get("address")
    if got != address:
        return (f"FAIL: the lease handed out {got:#x}, not the {address:#x} "
                "its transaction validated")
    return "ok"


def test_generated_call_uses_the_leased_pointer() -> str:
    """B5-1 on the receiver of a generated call. See README."""
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    parent = sample.ObjectType()
    child = sample.ObjectType()
    child.setObjectName("leased")
    child.setParent(parent)
    # objectTypeHash() hands back an unsigned int, so the comparison is
    # against the low half of the address, not the whole of it.
    address = Shiboken.getCppPointer(child)[0] & 0xffffffff
    result = {}

    with Failpoint("lease-after-acquire") as point:
        def call():
            try:
                result["hash"] = hash(child)
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        caller = threading.Thread(target=call)
        caller.start()
        if not point.wait_until_reached():
            return "FAIL: the call never reached the failpoint"

        parent.killChild("leased")

        point.release()
        caller.join(timeout=5)
        if caller.is_alive():
            return "FAIL: the calling thread did not come back"

    if "error" in result:
        return f"FAIL: the leased call raised {result['error']}"
    got = result.get("hash")
    if got != address:
        return (f"FAIL: the call ran on {got:#x}, not on the {address:#x} "
                "its lease validated")
    return "ok"


# Objects that have to outlive the test that made them.
_KEEP_ALIVE = []


def test_derived_metatype_takes_a_lease() -> str:
    """A wrapper whose class brings a metaclass of its own. See README."""
    class OwnMeta(type(QObject)):
        pass

    class Subclassed(QObject, metaclass=OwnMeta):
        pass

    obj = Subclassed()
    # Kept alive on purpose: destroying such a type crashes.
    # See README.
    _KEEP_ALIVE.append(obj)
    address = Shiboken.getCppPointer(obj)[0]
    result = {}

    with Failpoint("lease-after-acquire") as point:
        def read():
            try:
                result["address"] = int(Shiboken.VoidPtr(obj))
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        reader = threading.Thread(target=read)
        reader.start()
        reached = point.wait_until_reached()
        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"

    if not reached:
        return "FAIL: the read took no lease, so it never reached the failpoint"
    if "error" in result:
        return f"FAIL: the leased read raised {result['error']}"
    got = result.get("address")
    if got != address:
        return (f"FAIL: the lease handed out {got:#x}, not the {address:#x} "
                "the wrapper holds")
    return "ok"


def test_claim_follows_a_child_that_moves_out() -> str:
    """B6-1: a child that leaves a claimed parent. See README."""
    qt_app()
    parent = QObject()
    child = QObject()
    child.setObjectName("child")
    child.setParent(parent)

    # Bound before arming: the lookup takes a lease of its own.
    # See lease-vs-destroy.
    detach = child.setParent

    with Failpoint("lease-after-acquire") as point:
        mover = threading.Thread(target=lambda: detach(None))
        mover.start()
        if not point.wait_until_reached():
            return "FAIL: the reparenting call never reached the failpoint"

        # The graph still reads parent -> child: the destruction is put aside.
        Shiboken.delete(parent)

        point.release()
        mover.join(timeout=5)
        if mover.is_alive():
            return "FAIL: the reparenting thread did not come back"

    # The lease release ran the destruction, with the child out of the set.
    if Shiboken.isValid(parent):
        return "FAIL: the parent survived its own deletion"
    # Asked before calling anything: a refused wrapper would raise.
    if not Shiboken.isValid(child):
        return ("FAIL: the child that moved out is refused - it carries the "
                "claim of a parent it no longer has")
    if child.parent() is not None:
        return "FAIL: the child is still in the parent it left"
    answered = child.objectName()
    if answered != "child":
        return f"FAIL: the child answers {answered!r}"
    Shiboken.delete(child)
    if Shiboken.isValid(child):
        return "FAIL: the child that moved out cannot be deleted either"
    return "ok"


def test_claim_survives_a_teardown_detach() -> str:
    """B6-1, the other direction: a teardown detach keeps the claim. See README."""
    try:
        import sample
    except ImportError:
        return "skipped: this build has no sample binding"

    class Sub(sample.ObjectType):    # containsCppWrapper: stays valid
        pass

    root = sample.ObjectType.create()   # C++ built it: no wrapper of its own
    child = Sub()
    child.setParent(root)
    # The stamp has to reach the grandchild too.
    # See README.
    grand = Sub()
    grand.setParent(child)

    # Bound before the point is armed, as lease-vs-destroy explains.
    call = child.objectName

    with Failpoint("lease-after-acquire") as point:
        holder = threading.Thread(target=call)
        holder.start()
        if not point.wait_until_reached():
            return "FAIL: the leased call never reached the failpoint"

        # A lease is open in the set: the destruction waits, the child derives.
        Shiboken.delete(root)
        derived = not Shiboken.isValid(child)

        # Invalidated without extraction: the children are handed back.
        Shiboken.invalidate(root)
        kept = not Shiboken.isValid(child)

        point.release()
        holder.join(timeout=5)
        if holder.is_alive():
            return "FAIL: the leased call did not come back"

    # Asked once no claim waits and nothing is derived any more.
    kept_deep = not Shiboken.isValid(grand)

    if not derived:
        return "FAIL: the child never derived the waiting claim"
    if not kept:
        return ("FAIL: the child lost the claim when its parent was torn "
                "down - a lease on it would be granted while that parent's "
                "destructor takes its C++ instance")
    if not kept_deep:
        return ("FAIL: the grandchild lost the claim once the last one "
                "stopped waiting - the stamp reached its parent and left "
                "it to a derivation that is no longer made")
    return "ok"


def test_setter_conversion_fails() -> str:
    """B10-3: a field setter whose argument dies during the conversion. See README."""
    try:
        from sample import Derived, ObjectType
    except ImportError:
        return "skipped: the sample binding is not in this build"

    holder = Derived()
    kept = ObjectType()
    holder.objectTypeField = kept
    doomed = ObjectType()
    outcome = {}

    with Failpoint("convert-before-lease") as point:
        def assign():
            try:
                holder.objectTypeField = doomed
            except BaseException as exc:          # noqa: BLE001
                outcome["error"] = repr(exc)

        setter = threading.Thread(target=assign)
        setter.start()
        if not point.wait_until_reached():
            return "FAIL: the setter never reached the failpoint"

        Shiboken.delete(doomed)

        point.release()
        setter.join(timeout=5)
        if setter.is_alive():
            return "FAIL: the setting thread did not come back"

    now = holder.objectTypeField
    if now is not kept:
        return f"FAIL: the field became {now!r} although the conversion failed"
    if "error" not in outcome:
        return "FAIL: the setter reported success with the conversion failed"
    return f"ok - the field kept its value, {outcome['error'][:44]}"


def test_owned_child_is_claimed_while_the_parent_dies() -> str:
    """A child with a C++ wrapper must be refused while its parent dies. See README."""
    qt_app()
    parent = QObject()
    child = QObject(parent)
    child.setObjectName("owned")

    seen = None
    with Failpoint("delete-before-owned-dtor") as point:
        worker = threading.Thread(target=lambda: Shiboken.delete(parent))
        worker.start()
        if not point.wait_until_reached():
            return "FAIL: the deletion never reached the failpoint"

        # Detached, not yet destroyed: only the claim refuses the child here.
        seen = Shiboken.isValid(child)

        point.release()
        worker.join(timeout=5)
        if worker.is_alive():
            return "FAIL: the deleting thread did not come back"

    if seen:
        return ("FAIL: the child was usable while its parent's destructor "
                "was still to run - the owned set carries no claim")
    return "ok - the child is refused while the parent dies"


def test_parent_removal_allocation_fails() -> str:
    """B6-4: the deferred slot of a parent removal fails to allocate. See README."""
    parent = QObject()
    child = QObject(parent)
    if Shiboken.ownedByPython(child):
        return "FAIL: the child was not owned by its parent to begin with"

    error = None
    with FailpointThrow("deferred-slot-alloc"):
        try:
            child.setParent(None)
        except BaseException as exc:          # noqa: BLE001
            error = repr(exc)

    if error is None:
        return "FAIL: the failing allocation was not reported"
    if Shiboken.ownedByPython(child):
        return (f"FAIL: ownership moved although the transaction failed "
                f"({error[:40]})")
    # Unarmed now: a transaction that left nothing behind runs again.
    child.setParent(None)
    if not Shiboken.ownedByPython(child):
        return "FAIL: the retry did not hand ownership back"
    return f"ok - ownership survived the failure, {error[:40]}"


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
    """Open, owned by the lazy protocol: B13-5 from the destruction end.

    Module::get() holds the lazy-type mutex across PyObject_GetAttr(), so
    arbitrary Python runs under it - and with it a refcount reaching zero, a
    wrapper being destroyed, a deferred C++ destructor running, which is what
    DeferredActions::run() declares no raw lock may span.

    The two drivers below reached that shape when this was written and no
    longer do; the defect did not go away with them. So a run without a
    recorded exception has measured nothing, and says so rather than green -
    the one thing this test must not do is claim the lazy protocol is sound.
    """
    if not FREE_THREADED:
        return "skipped: a build with a GIL takes no lazy-type lock"

    test_no_raw_lock_while_python_runs()
    test_no_leaked_lease()

    # Only the lazy line: the wrapper-map exception is a different, documented
    # one, taken on every type-narrowed lookup.
    taken = [line for line in Shiboken.contractExceptions().split("\n")
             if line.startswith("lazy type")]
    if taken:
        return f"FAIL: the contract's exception was taken -> {'; '.join(taken)}"
    return "skipped: nothing was destroyed under the lazy-type lock in this run"


def test_metaobject_lifetime() -> str:
    """A shared wrapper invalidated by a stranger's destruction.

    Every QObject answers metaObject() with the same &QObject::staticMetaObject,
    so the map holds exactly one wrapper for it and every instance hands out
    that one. Destroying any single QObject invalidated it, and every other
    holder was hit.

    Not free-threading: five lines with a GIL and no threads. The third line
    is the whole test - without it the shared wrapper is not among b's
    referred objects, nothing touches it, and the four remaining lines pass
    on a broken build:

        a, b = QObject(), QObject()
        ma = a.metaObject()
        mb = b.metaObject()         # the SAME wrapper, fetched through b
        Shiboken.delete(b)          # a stranger
        ma.className()              # RuntimeError: already deleted

    Bisected to 4c1d56fb6 (29.07.2026), which moved the bookkeeping in
    callCppDestructors() ahead of the C++ destructors - before that,
    clearReferences() had taken the referred objects out before invalidate()
    ran. That only exposed it: invalidate() had walked referred objects since
    2011, and a referred object is by definition one the holder does not own.
    The walk is gone now, in both twins.
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


def test_metaobject_commit_race() -> str:
    """B15-1/B15-2: two threads build one object's instance meta object.

    Parsing the Python type moved out of the meta-object lock, which opens a
    window between the lookup that misses and the commit that publishes: both
    threads build a candidate there, and one of them has to give its own back
    and continue with the winner's. Without the failpoint that window is a
    few microseconds wide and a stress run reaches it by luck.

    What this can see afterwards: both signals in one meta object, at
    distinct indexes, and exactly two methods added to the class - which is
    what a second surviving builder would break, because the loser would
    carry its own signal and the winner would not have it.

    What it cannot see: whether the loser's candidate was freed. That is a
    heap question, and this harness counts crashes.
    """
    class Sender(QObject):
        pass

    class Receiver(QObject):
        def receiver(self):
            pass

    sender = Sender()
    receiver = Receiver()
    # The class meta object, before any instance added to it.
    base_methods = Sender.staticMetaObject.methodCount()
    connected: dict[str, bool] = {}

    def connect(name: str) -> None:
        connected[name] = QObject.connect(sender, SIGNAL(f"{name}()"),
                                          receiver, SLOT("receiver()"))

    with Failpoint("metaobject-before-commit") as point:
        parked = threading.Thread(target=connect, args=("alpha",))
        parked.start()
        if not point.wait_until_reached():
            return "FAIL: no thread parked before the commit"
        # The arming goes with the first thread, so this one runs through,
        # builds its own candidate and publishes it.
        connect("beta")
        if not point.release():
            return "FAIL: nobody was parked to release"
        parked.join(timeout=10)
        if parked.is_alive():
            return "FAIL: the parked thread did not come back"

    if not all(connected.values()):
        return f"FAIL: a connection did not take: {connected}"
    meta = sender.metaObject()
    indexes = {name: meta.indexOfSignal(f"{name}()") for name in connected}
    if any(index < 0 for index in indexes.values()):
        return f"FAIL: a signal is not in the meta object: {indexes}"
    if len(set(indexes.values())) != len(indexes):
        return f"FAIL: two signals share one index: {indexes}"
    added = meta.methodCount() - base_methods
    if added != len(connected):
        return (f"FAIL: {added} method(s) added for {len(connected)} "
                "signal(s) - a candidate was registered twice, or a "
                "second builder survived")
    return f"ok (both signals in one meta object, {indexes})"


def _parked_virtual(cls, pool):
    """Start one runnable of cls on a pool thread, to park in getOverride()."""
    work = cls()
    work.setAutoDelete(False)
    pool.start(work)
    return work


def test_mro_snapshot_is_owned() -> str:
    """FT3: the walk in getOverride() owns the tuple it walks. See README."""
    import sys
    from PySide6.QtCore import QRunnable, QThreadPool
    qt_app()

    ran = threading.Event()

    class Work(QRunnable):
        def run(self):
            ran.set()

    pool = QThreadPool.globalInstance()
    with Failpoint("mro-after-snapshot", timeout_ms=30000) as point:
        _parked_virtual(Work, pool)
        if not point.wait_until_reached():
            return "FAIL: the virtual never reached the failpoint"
        parked = sys.getrefcount(Work.__mro__)
        point.release()
        if not pool.waitForDone(30000):
            return "FAIL: the pool thread did not come back"
    released = sys.getrefcount(Work.__mro__)

    if not ran.is_set():
        return "FAIL: the override never ran, so nothing walked the mro"
    if parked <= released:
        return (f"FAIL: the parked walk held no reference to __mro__ "
                f"({parked} parked, {released} afterwards)")
    return (f"ok (the parked walk held {parked - released} reference(s) to "
            f"__mro__ that the finished walk gave back)")


def test_mro_snapshot_survives_bases_swap() -> str:
    """FT3: __bases__ is assigned under a virtual's mro walk. See README."""
    from PySide6.QtCore import QRunnable, QThreadPool
    qt_app()

    ran = threading.Event()

    class Mid1(QRunnable):
        pass

    class Mid2(QRunnable):
        pass

    class Work(Mid1):
        def run(self):
            ran.set()

    # A walk that strays into a decoy finds run() as an inherited default.
    decoy = type("Decoy", (object,), {"run": Work.run})
    width = len(Work.__mro__)

    pool = QThreadPool.globalInstance()
    with Failpoint("mro-after-snapshot", timeout_ms=30000) as point:
        _parked_virtual(Work, pool)
        if not point.wait_until_reached():
            return "FAIL: the virtual never reached the failpoint"

        Work.__bases__ = (Mid2,)
        # Required: only the tracing collector frees a deferred-refcount mro.
        gc.collect()
        ballast = [tuple([decoy] * width) for _ in range(2000)]

        point.release()
        if not pool.waitForDone(30000):
            return "FAIL: the pool thread did not come back"

    if not ran.is_set():
        return ("FAIL: the override did not run - the walk resolved against "
                "something other than the mro it started on")
    return (f"ok (__bases__ swapped, old mro collected and {len(ballast)} "
            f"decoys allocated over it, the walk still found the override)")


def test_bases_snapshot_survives_bases_swap() -> str:
    """FT3: __bases__ is assigned under a property lookup. See README."""
    from PySide6.QtCore import Property
    qt_app()

    class Holder(QObject):
        @Property(int)
        def val(self):
            return 7

    class Other(QObject):
        pass

    class Sub(Holder):
        pass

    obj = Sub()
    answer = []

    def ask():
        answer.append(obj.property("val"))

    decoy = type("Decoy", (object,), {})
    with Failpoint("bases-after-snapshot", timeout_ms=30000) as point:
        asker = threading.Thread(target=ask)
        asker.start()
        if not point.wait_until_reached():
            return "FAIL: the property lookup never reached the failpoint"

        Sub.__bases__ = (Other,)
        # No collection needed: the old bases tuple falls at once.
        ballast = [(decoy,) for _ in range(2000)]

        point.release()
        asker.join(timeout=30)
        if asker.is_alive():
            return "FAIL: the asking thread did not come back"

    if answer != [7]:
        return (f"FAIL: the lookup answered {answer}, not [7] - it resolved "
                f"against something other than the bases it started on")
    return (f"ok (__bases__ swapped, old tuple released and {len(ballast)} "
            f"decoys allocated over it, the walk still found the property)")


def test_shadowed_mro_is_not_dropped() -> str:
    """A metaclass answers __mro__ with an unshared tuple. See README."""
    if not FREE_THREADED:
        return "skipped: the holder has one path in a build with a GIL"

    class ShadowMeta(type(QObject)):
        @property
        def __mro__(cls):
            # A fresh tuple per access, held by nobody else, valid to walk.
            return (cls, QObject, object)

    class Shadowed(QObject, metaclass=ShadowMeta):
        pass

    # Kept alive on purpose: destroying such a type crashes.
    # See README.
    _KEEP_ALIVE.append(Shadowed())

    # The preconditions, asked directly: sys.getrefcount() cannot say
    # "one owner" on this build.
    real = type.__dict__["__mro__"].__get__(Shadowed)
    shadowing = Shadowed.__mro__ is not real
    fresh = Shadowed.__mro__ is not Shadowed.__mro__

    # QObject.tr() walks the mro in qObjectTr().
    answers = {Shadowed.tr("some text") for _ in range(50)}

    if not shadowing:
        return ("FAIL: __mro__ still answers the type's own tuple, so this "
                "run is not asking what it was written for")
    if not fresh:
        return ("FAIL: the descriptor hands out the same tuple twice, so "
                "something holds it and dropping it would be harmless")
    if answers != {"some text"}:
        return f"FAIL: tr() answered {answers}, not the source text"
    return ("ok (50 walks over a tuple built per access and held by nobody, "
            "none of them dropped it)")


def test_a_failed_override_lookup_is_not_cached() -> str:
    """A failed mro lookup is not cached as "no override". See README."""
    if not FREE_THREADED:
        return "skipped: the free-threaded cache is what this asks about"
    from PySide6.QtCore import QRunnable, QThreadPool

    # Armed only after the class exists: creating it reads __mro__.
    failing = [False]

    class RaisingMeta(type(QObject)):
        @property
        def __mro__(cls):
            if failing[0]:
                failing[0] = False
                raise MemoryError("once, on purpose")
            return type.__dict__["__mro__"].__get__(cls)

    ran = []

    class Work(QRunnable, metaclass=RaisingMeta):
        def run(self):
            ran.append(1)

    _KEEP_ALIVE.append(Work)
    # The instance too, so that the raise lands in the override lookup.
    work = Work()
    work.setAutoDelete(False)
    _KEEP_ALIVE.append(work)

    pool = QThreadPool.globalInstance()
    failing[0] = True
    for _ in range(2):
        pool.start(work)
        if not pool.waitForDone(30000):
            return "FAIL: the pool thread did not come back"

    if failing[0]:
        return "FAIL: the lookup never reached the raising metaclass"
    if not ran:
        return ("FAIL: the override never ran - the failed lookup was "
                "cached as 'no override'")
    return (f"ok (the first lookup raised, the override ran {len(ran)} "
            f"time(s) afterwards)")


def _cpp_deleted(obj) -> bool:
    """Whether the wrapper has lost its C++ object. Takes no lease, so it
    answers for a claimed object too, where isValid() says False either way."""
    return "<<Deleted>>" in Shiboken.dump(obj)


def _binding_parent(obj) -> str | None:
    """The address of the parent in the binding graph, as dump() prints it."""
    for line in Shiboken.dump(obj).splitlines():
        if line.startswith("parent"):
            return line.rsplit(" at ", 1)[1].rstrip(">")
    return None


def test_container_element_lease_is_kept() -> str:
    """An element of a container argument is deleted mid-call. See README."""
    if not FREE_THREADED:
        return "skipped: a build with a GIL has no conversion leases"
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    parked = threading.Event()
    go = threading.Event()
    seen: dict[str, object] = {}

    class Parker(sample.ObjectType):
        def event(self, event):
            parked.set()
            # No timeout: a parker that gave up would run the victim's call
            # on freed memory.
            go.wait()
            return True

    class Victim(sample.ObjectType):
        def event(self, event):
            seen["alive"] = not _cpp_deleted(self)
            return True

    parker, victim = Parker(), Victim()

    def call():
        try:
            seen["count"] = sample.ObjectType.processEvent(
                [parker, victim], sample.Event(sample.Event.BASIC_EVENT))
        except BaseException as exc:      # noqa: BLE001
            seen["error"] = repr(exc)

    # A daemon, because the failure below leaves it parked on purpose.
    caller = threading.Thread(target=call, daemon=True)
    caller.start()
    if not parked.wait(timeout=5):
        go.set()
        return "FAIL: the first element's event() never ran"

    # The list was converted; only the kept leases stand between this delete
    # and the pointer processEvent() calls next.
    Shiboken.delete(victim)
    if _cpp_deleted(victim):
        # Not released: the native loop would call event() on freed memory.
        return ("FAIL: the element was destroyed while the call still held "
                "its pointer - its lease ended with the conversion")

    go.set()
    caller.join(timeout=5)
    if caller.is_alive():
        return "FAIL: the calling thread did not come back"
    if "error" in seen:
        return f"FAIL: processEvent() raised {seen['error']}"
    if seen.get("count") != 2 or not seen.get("alive"):
        return (f"FAIL: the second element was not called on a live object "
                f"(count {seen.get('count')}, alive {seen.get('alive')})")
    if not _cpp_deleted(victim):
        return "FAIL: the deferred delete never ran after the call"
    return "ok - the delete waited for the call that held the element"


def test_dealloc_waits_for_a_child_lease() -> str:
    """A parent's last reference goes while a call on its child is open. See README."""
    from PySide6.QtCore import Qt

    destroyed: list[int] = []
    # Created on this thread, so that the del below deallocates here.
    parent = QObject()
    child = QObject(parent)
    child.destroyed.connect(lambda: destroyed.append(threading.get_ident()),
                            Qt.ConnectionType.DirectConnection)
    address = Shiboken.getCppPointer(child)[0]
    result = {}

    with Failpoint("lease-after-acquire") as point:
        # VoidPtr and not a method: it copies the pointer and reads nothing
        # behind it, so the run without the bit reports instead of crashing.
        def read():
            try:
                result["address"] = int(Shiboken.VoidPtr(child))
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        reader = threading.Thread(target=read)
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the read never reached the failpoint"

        del parent
        during = list(destroyed)

        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"

    if during:
        return ("FAIL: the parent's destructor took the child while a call "
                "on it held a lease")
    if "error" in result:
        return f"FAIL: the leased read raised {result['error']}"
    if result.get("address") != address:
        return f"FAIL: the lease handed out {result.get('address')!r}"
    if destroyed != [reader.ident]:
        return (f"FAIL: the destructor did not run once, from the lease "
                f"release (ran on {destroyed}, reader {reader.ident})")
    if Shiboken.isValid(child):
        return "FAIL: the child is still valid after its parent's destructor"
    return "ok - the destructor waited and ran from the lease release"


def test_dealloc_claim_releases_a_survivor() -> str:
    """A child the parent's destructor leaves alive stays usable. See README."""
    if not fp.QML_READY:
        return "skipped: QtQml not available"
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent

    engine = qml_engine()

    def create():
        component = QQmlComponent(engine)
        component.setData(b"import QtQml\nimport FailpointTest 1.0\nPlaced { }",
                          QUrl())
        return component, component.create()

    # No lease open: the destructor runs inside the deallocator.
    component, inline = create()
    del component

    # A lease open on the survivor: the destructor waits for it.
    component, waited = create()
    result = {}
    with Failpoint("lease-after-acquire") as point:
        def read():
            try:
                result["address"] = int(Shiboken.VoidPtr(waited))
            except BaseException as exc:      # noqa: BLE001
                result["error"] = repr(exc)

        reader = threading.Thread(target=read)
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the read never reached the failpoint"
        del component
        # Shows that this half took the waiting path at all.
        refused = not Shiboken.isValid(waited)
        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"

    if "error" in result:
        return f"FAIL: the leased read raised {result['error']}"
    if not refused:
        return "FAIL: the survivor was not claimed while the destructor waited"
    for how, obj in (("inline", inline), ("after the lease", waited)):
        if obj is None:
            return f"FAIL: QML created nothing ({how})"
        if not Shiboken.isValid(obj):
            return (f"FAIL: the survivor of a destructor run {how} is still "
                    "refused - the claim was not taken back")
        if obj.objectName() != "placed":
            return f"FAIL: the survivor ({how}) answers {obj.objectName()!r}"
    return "ok - both survivors are usable once the destructor is past"


def test_teardown_detaches_only_its_own_edge() -> str:
    """A child is reparented in the middle of its parent's teardown. See README."""
    try:
        import sample
    except ImportError:
        return "skipped: the sample binding is not in this build"

    root = sample.ObjectType()
    # Built from Python, so its destructor reports through Object::destroy().
    doomed = sample.ObjectType()
    doomed.setObjectName("doomed")
    doomed.setParent(root)
    child = sample.ObjectType()
    child.setParent(doomed)
    rescuer = sample.ObjectType()
    del doomed                     # root holds it
    # Bound before arming, as lease-vs-destroy explains.
    move = child.setParent

    with Failpoint("detach-mid-round") as point:
        killer = threading.Thread(target=lambda: root.killChild("doomed"))
        killer.start()
        if not point.wait_until_reached():
            return "FAIL: the teardown never reached the failpoint"

        # In C++ as well: the destructor still to run no longer takes it.
        move(rescuer)

        point.release()
        killer.join(timeout=5)
        if killer.is_alive():
            return "FAIL: the tearing-down thread did not come back"

    parent = _binding_parent(child)
    if parent != hex(id(rescuer)):
        return (f"FAIL: the teardown removed the child's new edge (binding "
                f"parent {parent}, rescuer {hex(id(rescuer))})")

    # What the edge is for: deleting the new parent waits for a call on it.
    with Failpoint("lease-after-acquire") as point:
        reader = threading.Thread(target=lambda: Shiboken.VoidPtr(child))
        reader.start()
        if not point.wait_until_reached():
            return "FAIL: the read never reached the failpoint"
        Shiboken.delete(rescuer)
        early = _cpp_deleted(child)
        point.release()
        reader.join(timeout=5)
        if reader.is_alive():
            return "FAIL: the reading thread did not come back"

    if early:
        return "FAIL: deleting the new parent did not wait for the child's lease"
    if not _cpp_deleted(child):
        return "FAIL: the child outlived the deferred delete of its parent"
    return "ok - the new edge survived the teardown and still defers a delete"


def test_constructor_leases_its_tail() -> str:
    """A delete between a constructor's commit and its QObject setup. See README."""
    shared: list[QObject] = []
    seen: dict[str, object] = {}

    class Published(QObject):
        def __init__(self):
            # Where another thread finds it before the base __init__ is done.
            shared.append(self)
            try:
                # A keyword, so the setup also reads metaObject() and fills
                # properties. Not objectName: its generated setter takes a
                # lease, which the waiting delete refuses.
                super().__init__(tag="published")
            except BaseException as exc:      # noqa: BLE001
                seen["error"] = repr(exc)
                return
            seen["done"] = True

        def setTag(self, value):
            # Called by fillQtProperties(), under the constructor's lease.
            seen["alive in setup"] = not _cpp_deleted(self)

    name = "ctor-after-publish"
    # Armed by hand, not with Failpoint: on the failing path the constructor
    # has to stay parked, and the timeout has to outlast the process.
    if not Shiboken.armFailpoint(name, 120_000):
        raise fp.FailpointMissing(name)
    # A daemon, because the failure below leaves it parked on purpose.
    builder = threading.Thread(target=Published, daemon=True)
    builder.start()
    if not Failpoint(name).wait_until_reached():
        Shiboken.clearFailpoints()
        return "FAIL: the constructor never reached the failpoint"

    victim = shared[0]
    Shiboken.delete(victim)
    if _cpp_deleted(victim):
        # Not released: the setup would read metaObject() from freed memory.
        return ("FAIL: the object was destroyed while its constructor was "
                "parked - no lease covers the QObject setup")

    Shiboken.releaseFailpoint(name)
    builder.join(timeout=5)
    Shiboken.clearFailpoints()
    if builder.is_alive():
        return "FAIL: the constructing thread did not come back"
    if "error" in seen:
        return f"FAIL: __init__ raised {seen['error']}"
    if not seen.get("done"):
        return "FAIL: __init__ did not complete"
    if not seen.get("alive in setup"):
        return (f"FAIL: the property setup ran on a destroyed object "
                f"(alive {seen.get('alive in setup')})")
    if not _cpp_deleted(victim):
        return "FAIL: the deferred delete never ran after the constructor"
    return "ok - the delete waited for the constructor's QObject setup"


TESTS = {
    "weakrefs": Test(test_weakrefs_while_deallocating),
    # Was an expected FAIL on a wrong explanation; see the docstring.
    "lease-vs-destroy": Test(test_destroy_while_call_in_flight),
    # A guard, no proof-* row: see the README.
    "teardown-vs-call": Test(test_teardown_waits_for_a_call_in_flight),
    "deferred-widget-dtor": Test(test_deferred_widget_destruction_in_main_thread),
    "dict-first-access": Test(test_dict_first_access),
    "proof-dict-first-access": Test(lambda: counterproof(
        "DictPublishOnce", "dict-first-access")),
    "dict-survives-clear": Test(test_dict_survives_clear),
    "proof-dict-survives-clear": Test(lambda: counterproof(
        "DictPublishOnce", "dict-survives-clear")),
    "claim-moves-out": Test(test_claim_follows_a_child_that_moves_out),
    "proof-claim-ancestry": Test(lambda: counterproof("ClaimByAncestry",
                                                      "claim-moves-out")),
    "claim-survives-teardown": Test(test_claim_survives_a_teardown_detach),
    # Its own bit: without ClaimByAncestry this row would pass.
    # See README.
    "proof-claim-teardown": Test(lambda: counterproof("ClaimThroughTeardown",
                                                      "claim-survives-teardown")),
    "replacement-while-dying": Test(test_replacement_wrapper_while_dying),
    "setter-conversion-fails": Test(test_setter_conversion_fails),
    "proof-conversion-gate": Test(lambda: counterproof(
        "ConversionGate", "setter-conversion-fails")),
    # No proof-* row, on purpose.
    # See the README.
    "owned-child-claimed": Test(test_owned_child_is_claimed_while_the_parent_dies),
    "parent-removal-alloc": Test(test_parent_removal_allocation_fails),
    "proof-transaction-prepare": Test(lambda: counterproof(
        "TransactionPrepare", "parent-removal-alloc")),
    "two-thread-ctor": Test(test_two_threads_one_constructor),
    "lease-snapshot": Test(test_lease_carries_the_pointer_it_validated),
    "proof-lease-snapshot": Test(lambda: counterproof(
        "LeaseSnapshot", "lease-snapshot")),
    # No proof-* row, on purpose.
    # See the README.
    "mi-pointer": Test(test_multiple_inheritance_pointer),
    # A guard, no proof-* row: see the README.
    "signal-type-collectable": Test(test_signal_instance_leaves_its_type_collectable),
    "capsule-method-owns-instance": Test(test_capsule_method_owns_its_instance),
    "capsule-access-no-leak": Test(test_capsule_access_does_not_leak),
    "source-property-copy": Test(test_source_property_read_as_copy),
    "proof-source-property-copy": Test(lambda: counterproof(
        "SourcePropertyCopy", "source-property-copy")),
    "source-property-missing": Test(test_source_without_property_list),
    "metaclass-tuples": Test(test_metaclass_tuples_are_checked),
    "signal-homonym": Test(test_signal_homonym_owned),
    "leased-receiver": Test(test_generated_call_uses_the_leased_pointer),
    "proof-leased-receiver": Test(lambda: counterproof(
        "LeaseSnapshot", "leased-receiver")),
    "metatype-subclass": Test(test_derived_metatype_takes_a_lease),
    "proof-metatype-subclass": Test(lambda: counterproof(
        "MetatypeSubclassLease", "metatype-subclass")),
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
    "mro-snapshot-owns": Test(test_mro_snapshot_is_owned),
    "mro-snapshot": Test(test_mro_snapshot_survives_bases_swap),
    # Counter-proof for the window (mro-snapshot), not the refcount.
    "proof-mro-snapshot": Test(lambda: counterproof("MroSnapshot",
                                                    "mro-snapshot")),
    "bases-snapshot": Test(test_bases_snapshot_survives_bases_swap),
    # No proof-* rows for these two.
    # See README.
    "shadowed-mro": Test(test_shadowed_mro_is_not_dropped),
    "failed-override-lookup": Test(test_a_failed_override_lookup_is_not_cached),
    # The same bit on the other field.
    "proof-bases-snapshot": Test(lambda: counterproof("MroSnapshot",
                                                      "bases-snapshot")),
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
    # Not free-threading: the same defect is five lines with a GIL, see the
    # docstring. Kept because this is where it was found.
    "metaobject-lifetime": Test(test_metaobject_lifetime),
    # Known open, owned by the lazy protocol's replacement: the lazy-type lock
    # spans type creation, and a deferred destructor runs under it. A run that
    # does not reach that shape skips, see the docstring.
    "lazy-lock-spans-destruction": Test(test_lazy_lock_spans_destruction, "FAIL"),
    "metaobject-commit-race": Test(test_metaobject_commit_race),
    # Without the bit the parse goes back under the meta-object lock, and the
    # contract assertion at the top of parsePythonType() aborts before the
    # failpoint is ever reached. The abort is the answer: it says this path
    # runs the interpreter with a binding raw lock held.
    "proof-metaobject-parse": Test(lambda: counterproof(
        "MetaObjectParseOutsideLock", "metaobject-commit-race")),
    "container-element-lease": Test(test_container_element_lease_is_kept),
    "proof-conversion-leases": Test(lambda: counterproof(
        "ConversionLeasesKept", "container-element-lease")),
    "dealloc-waits-for-lease": Test(test_dealloc_waits_for_a_child_lease),
    "proof-dealloc-claim": Test(lambda: counterproof(
        "DeallocClaim", "dealloc-waits-for-lease")),
    # No proof-* row, on purpose.
    # See the README.
    "dealloc-claim-survivor": Test(test_dealloc_claim_releases_a_survivor),
    "teardown-detach-edge": Test(test_teardown_detaches_only_its_own_edge),
    "proof-detach-checked-parent": Test(lambda: counterproof(
        "DetachCheckedParent", "teardown-detach-edge")),
    "constructor-tail-lease": Test(test_constructor_leases_its_tail),
    "proof-constructor-tail-lease": Test(lambda: counterproof(
        "ConstructorTailLease", "constructor-tail-lease")),
}


if __name__ == "__main__":
    sys.exit(fp.main(TESTS))
