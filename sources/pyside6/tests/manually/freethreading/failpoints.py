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


def test_destroy_while_call_in_flight() -> str:
    """The lease window: destruction arriving while a call holds a lease."""
    obj = QObject()
    obj.setObjectName("leased")
    result = {}

    with Failpoint("lease-after-acquire") as point:
        def call():
            try:
                result["name"] = obj.objectName()
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
    """Open: metaObject() hands out a wrapper it does not keep alive."""
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
    # Known open: FT4 owns the lease duration, and the generated code re-reads
    # cppSelf after the lease was granted. The lease does hold the C++
    # destructor off - ASan finds no use-after-free - but the call refuses.
    "lease-vs-destroy": Test(test_destroy_while_call_in_flight, "FAIL"),
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
    # Known open, free-threading-specific: 3 failures out of 600 without the
    # GIL, 0 with it on the same binary. The lease work owns it.
    "metaobject-lifetime": Test(test_metaobject_lifetime, "FAIL"),
    # Known open, owned by the lazy protocol's replacement: the lazy-type lock
    # spans type creation, and a deferred destructor runs under it.
    "lazy-lock-spans-destruction": Test(test_lazy_lock_spans_destruction, "FAIL"),
}


if __name__ == "__main__":
    import sys
    sys.exit(fp.main(TESTS))
