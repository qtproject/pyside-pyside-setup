#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""
Free-threading stress worker (PoC).

Runs ONE scenario as hard as possible from many threads with the real GIL
disabled, exercising exactly the shiboken per-object state that the state
lock protects: the wrapper lifecycle, ownership flags and call leases.

A scenario belongs here only if it races shiboken's own bookkeeping on a
SHARED wrapper. Racing a shared C++ user object does not: mutating a
std::list from several threads is a defect in the calling code, and no
binding-level lock is meant to make it safe. Two such scenarios
(shared_parent, reparent, both hammering ObjectType::children) were dropped
for that reason - the coarse lock used to serialize them as a side effect,
which made them look like binding coverage.

Contract:
  * exit 0   -> survived cleanly
  * exit 3   -> a Python-level exception escaped (details on stderr)
  * killed by signal (SIGSEGV/SIGABRT) -> the C++ raced; the parent runner
    sees this as a negative return code == the real defect we hunt.

The locks are bits in PYSIDE6_OPTION_FT; which one a run clears depends on
the scenario, see run.py. This worker does not know or care which mode it
runs in; run.py drives the A/B.

Usage:  stress.py <scenario>   (THREADS / ITERS come from env)
"""

from __future__ import annotations

import os
import sys
import threading
import traceback
from pathlib import Path

# --- locate the built sample module via the standard test helper ------------
_REPO = Path(__file__).resolve().parents[5]
sys.path.append(os.fspath(_REPO / "sources" / "shiboken6" / "tests"))
from shiboken_paths import init_paths  # noqa: E402
init_paths()

from sample import ObjectType          # noqa: E402
from shiboken6 import Shiboken          # noqa: E402

THREADS = int(os.environ.get("STRESS_THREADS", "8"))
ITERS = int(os.environ.get("STRESS_ITERS", "6000"))

_failures: list[str] = []


def _spin(fn) -> None:
    """Start THREADS copies of fn, released simultaneously for max contention."""
    barrier = threading.Barrier(THREADS)

    def wrapped(idx: int) -> None:
        barrier.wait()
        try:
            fn(idx)
        except BaseException:  # noqa: BLE001
            _failures.append(traceback.format_exc())

    ts = [threading.Thread(target=wrapped, args=(i,)) for i in range(THREADS)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()


# --- scenarios --------------------------------------------------------------
# Each hammers a different guarded code path in basewrapper.cpp.

def scenario_destroy_race() -> None:
    """Many threads destroy parent objects that own a child.
    Races Object::destroy / deallocData / removeParent under the destructor."""
    def work(_idx: int) -> None:
        for _ in range(ITERS):
            o = ObjectType()
            c = ObjectType()
            c.setParent(o)          # child owned by parent
            Shiboken.delete(o)      # destroy parent -> must tear down child
    _spin(work)


def scenario_shared_delete(_pool=[]) -> None:  # noqa: B006
    """Many threads race to destroy the SAME wrapper objects.
    This hits shiboken's own locked paths (Object::destroy / deallocData /
    invalidate) on shared wrappers -- NOT libsample's C++ members -- so it is
    the honest test of the state lock. Deleting an already-invalidated
    wrapper must be a safe no-op; two threads doing it at once must not
    double-free."""
    POOL = 400
    if not _pool:
        _pool.extend(ObjectType() for _ in range(POOL))
    pool = _pool
    lock = threading.Lock()

    def work(idx: int) -> None:
        for i in range(ITERS):
            slot = (i * 7 + idx) % POOL
            obj = pool[slot]
            Shiboken.delete(obj)         # concurrent destroy of a shared wrapper
            if idx == 0:                 # one thread refills, racing the deleters
                with lock:
                    pool[slot] = ObjectType()
    _spin(work)


def scenario_call_vs_delete(_pool=[]) -> None:  # noqa: B006
    """Many threads call methods on the SAME wrapper while others destroy it.
    This is what the call lease exists for: a call that has passed the
    validity check must keep the C++ object alive until it returns, and the
    destruction must be deferred until the last lease is back. Calling a
    destroyed wrapper must raise RuntimeError, never crash."""
    # Small pool and every thread deleting: the point is that a call and a
    # destruction of the SAME wrapper overlap as often as possible.
    POOL = 32
    if not _pool:
        _pool.extend(ObjectType() for _ in range(POOL))
    pool = _pool

    def work(idx: int) -> None:
        for i in range(ITERS):
            slot = (i * 13 + idx) % POOL
            obj = pool[slot]
            try:
                obj.objectName()         # takes a call lease
                obj.setObjectName("x")
            except RuntimeError:
                pass                     # already deleted: the correct answer
            if i % 8 == idx % 8:
                Shiboken.delete(obj)     # races the callers above
                pool[slot] = ObjectType()  # list assignment is atomic
    _spin(work)


def scenario_child_delete_vs_call() -> None:
    """A parent is deleted, which deletes its child in C++; the child's wrapper
    enters Object::destroy() from that C++ destructor while other threads still
    call methods on the same child. Each producer owns its pair, so nothing of
    libsample is shared - only the child wrapper, which is the point."""
    SLOTS = 32
    kids: list[object] = [None] * SLOTS

    def work(idx: int) -> None:
        if idx % 2 == 0:
            for i in range(ITERS):
                slot = (i * 7 + idx) % SLOTS
                parent = ObjectType()
                child = ObjectType()
                child.setParent(parent)
                kids[slot] = child         # publish, then pull it away in C++
                Shiboken.delete(parent)
        else:
            for i in range(ITERS):
                child = kids[(i * 11 + idx) % SLOTS]
                if child is not None:
                    try:
                        child.objectName()
                        child.setObjectName("x")
                    except RuntimeError:
                        pass               # already destroyed: the right answer
    _spin(work)


def scenario_signal_race() -> None:
    """Threads connect Python slots to a few shared senders and let the
    receivers die again. connect() and the receiver teardown are hand-written
    libpyside code, so no generated call guard covers them; what protects the
    one global connection hash behind them is its own lock, and this inserts
    into it and erases from it at the same time."""
    from PySide6.QtCore import QObject, Signal

    class Emitter(QObject):
        fired = Signal(int)

    class Receiver(QObject):
        def on_fired(self, value: int) -> None:
            pass

    SENDERS = 4
    emitters = [Emitter() for _ in range(SENDERS)]

    def work(idx: int) -> None:
        for i in range(ITERS // 4):
            slot = (i + idx) % SENDERS
            # Replacing a sender erases its connections while others insert.
            if idx % 3 == 0:
                emitters[slot] = Emitter()
                continue
            emitter = emitters[slot]
            receiver = Receiver()
            try:
                emitter.fired.connect(receiver.on_fired)
                emitter.fired.emit(i)
            except RuntimeError:
                pass
            del receiver          # tears the connection out of the hash again
    _spin(work)


def scenario_lazy_converter() -> None:
    """Every thread converts a Str for the very first time at the same
    instant. The generated type initialization publishes the type into its
    TypeInitStruct before it registers the converter - deliberately, as the
    re-entrancy guard - so a second thread used to be handed a type whose
    converter was still null and died in copyToPython(). One round is enough:
    the window exists only while the type is being built."""
    obj = ObjectType()

    def work(_idx: int) -> None:
        for _ in range(20):
            obj.objectName()          # the first one incarnates Str
    _spin(work)


def scenario_lookup_vs_last_decref() -> None:
    """One thread drops the last reference to a wrapper while another looks the
    same C++ pointer up in the map, targeting the gap between the refcount
    reaching zero and tp_dealloc getting there. Before acquireWrapper() it
    crashed 30 times out of 30, clean since.

    Unlike the other scenarios the A/B here is the interpreter, not a lock: the
    decref that reaches zero happens in CPython, so no lock of ours could have
    closed the gap - it took a lookup that increments atomically. Nothing C++
    is shared; only an integer address travels between the threads.

    A crash inside libsample means the C++ object was gone before the lookup,
    which is a limit of the scenario rather than a defect.
    """
    SLOTS = 64
    addr: list[int] = [0] * SLOTS
    hold: list[object] = [None] * SLOTS

    def work(idx: int) -> None:
        if idx % 2 == 0:                      # produce and drop
            for i in range(ITERS):
                s = (i * 7 + idx) % SLOTS
                o = ObjectType.create()
                addr[s] = Shiboken.getCppPointer(o)[0]
                hold[s] = o
                hold[s] = None                # the last reference goes here
        else:                                 # look up the same address
            for i in range(ITERS):
                a = addr[(i * 11 + idx) % SLOTS]
                if a:
                    try:
                        Shiboken.wrapInstance(a, ObjectType)
                    except Exception:
                        pass
    _spin(work)


def scenario_shared_setter() -> None:
    """Every thread calls a setter on one shared object, and reads it back.

    Qt is not thread-safe per object and neither is libsample: two threads
    inside one C++ object at the same time is undefined, and with a GIL it
    simply never happened. The per-object call guard is what restores that,
    so this is the scenario for CallGuard - it has to crash with the guard
    switched off, or the guard is proving nothing.

    A QObject, not a libsample type: what has to be serialized is a Qt
    setter, and libsample's ObjectType is too simple to break. No
    wrapper-typed arguments on purpose - those take a lease without a guard,
    and this is about the receiver.
    """
    from PySide6.QtCore import QObject

    shared = QObject()

    def hammer(idx: int) -> None:
        for i in range(ITERS):
            shared.setObjectName(f"n{idx}-{i}")
            shared.objectName()

    _spin(hammer)


SCENARIOS = {
    "shared_setter": scenario_shared_setter,
    "destroy_race": scenario_destroy_race,
    "shared_delete": scenario_shared_delete,
    "call_vs_delete": scenario_call_vs_delete,
    "lazy_converter": scenario_lazy_converter,
    "child_delete_vs_call": scenario_child_delete_vs_call,
    "lookup_vs_last_decref": scenario_lookup_vs_last_decref,
    "signal_race": scenario_signal_race,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
        print(f"usage: stress.py {{{'|'.join(SCENARIOS)}}}", file=sys.stderr)
        return 64
    # sys._is_gil_enabled() only exists from 3.13 on; older interpreters
    # always have it, and are useful here as the serialized reference run.
    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
    gil = "ON" if gil_enabled else "off"
    ft = os.environ.get("PYSIDE6_OPTION_FT")
    locks = f"PYSIDE6_OPTION_FT={ft}" if ft else "all locks on"
    sys.stderr.write(f"[stress] {sys.argv[1]} gil={gil} {locks} "
                     f"threads={THREADS} iters={ITERS}\n")
    SCENARIOS[sys.argv[1]]()
    if _failures:
        sys.stderr.write(_failures[0])
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
