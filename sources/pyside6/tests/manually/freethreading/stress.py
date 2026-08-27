#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""
Free-threading stress worker (PoC).

Runs ONE scenario as hard as possible from many threads with the real GIL
disabled, exercising exactly the shiboken per-object state that the
CoarseBindingGuard protects: the parent-child graph and wrapper
destruction.

Contract:
  * exit 0   -> survived cleanly
  * exit 3   -> a Python-level exception escaped (details on stderr)
  * killed by signal (SIGSEGV/SIGABRT) -> the C++ raced; the parent runner
    sees this as a negative return code == the real defect we hunt.

The locks are toggled at runtime via the flags in env PYSIDE6_OPTION_FT. This worker
does not know or care which mode it runs in; run.py drives the A/B.

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

def scenario_shared_parent(_shared=[]) -> None:  # noqa: B006
    """Many threads insert AND remove children on the SAME parent.
    Races Object::setParent / removeParent / takeChild on one child list."""
    if not _shared:
        _shared.append(ObjectType())
    parent = _shared[0]

    def work(_idx: int) -> None:
        for _ in range(ITERS):
            c = ObjectType()
            c.setParent(parent)     # concurrent insert into parent->m_children
            parent.children()       # concurrent read of the list
            parent.takeChild(c)     # concurrent remove
            Shiboken.delete(c)
    _spin(work)


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


def scenario_reparent(_p=[]) -> None:  # noqa: B006
    """Many threads move children between two shared parents.
    Races two child lists + ownership transfer simultaneously."""
    if not _p:
        _p.extend([ObjectType(), ObjectType()])
    a, b = _p

    def work(idx: int) -> None:
        for i in range(ITERS):
            c = ObjectType()
            c.setParent(a)
            c.setParent(b)          # reparent: remove from a, insert into b
            b.takeChild(c)          # c is in b now -> detach from the RIGHT parent
            Shiboken.delete(c)      # no dangling child left in any parent
    _spin(work)


def scenario_shared_delete(_pool=[]) -> None:  # noqa: B006
    """Many threads race to destroy the SAME wrapper objects.
    This hits shiboken's own guarded paths (Object::destroy / deallocData /
    invalidate) on shared wrappers -- NOT libsample's C++ members -- so it is
    the honest test of the CoarseBindingGuard. Deleting an already-invalidated
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


SCENARIOS = {
    "shared_parent": scenario_shared_parent,
    "destroy_race": scenario_destroy_race,
    "reparent": scenario_reparent,
    "shared_delete": scenario_shared_delete,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
        print(f"usage: stress.py {{{'|'.join(SCENARIOS)}}}", file=sys.stderr)
        return 64
    gil = "off" if not sys._is_gil_enabled() else "ON"
    locks = os.environ.get("PYSIDE6_OPTION_FT", "default")
    sys.stderr.write(f"[stress] {sys.argv[1]} gil={gil} locks={locks} "
                     f"threads={THREADS} iters={ITERS}\n")
    SCENARIOS[sys.argv[1]]()
    if _failures:
        sys.stderr.write(_failures[0])
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
