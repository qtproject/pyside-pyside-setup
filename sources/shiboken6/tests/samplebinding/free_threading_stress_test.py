#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""Stress the object graph from many threads with the GIL disabled.

Each scenario hammers one of the paths that the coarse binding lock protects:
the parent/child bookkeeping and wrapper destruction. Without that lock these
scenarios segfault reliably, so a clean run is what keeps the lock honest.

The defaults are sized for CI. Set PYSIDE_STRESS_THREADS / PYSIDE_STRESS_ITERS
to hunt for races locally; tests/manually/freethreading/run.py drives the same
scenarios as an A/B proof against a build with the lock disabled at runtime.
"""

from __future__ import annotations

import os
import sys
import sysconfig
import threading
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType
from shiboken6 import Shiboken

THREADS = int(os.environ.get("PYSIDE_STRESS_THREADS", "8"))
ITERS = int(os.environ.get("PYSIDE_STRESS_ITERS", "1500"))

MSG_SKIP = "Only for GIL disabled builds."


def is_gil_disabled():
    gil_disabled_build = sysconfig.get_config_vars('Py_GIL_DISABLED')[0]
    return gil_disabled_build and not sys._is_gil_enabled()


@unittest.skipUnless(is_gil_disabled(), MSG_SKIP)
class ObjectGraphStressTest(unittest.TestCase):

    def spin(self, work):
        """Run work in THREADS threads, released together for contention."""
        failures = []
        barrier = threading.Barrier(THREADS)

        def wrapped(idx):
            barrier.wait()
            try:
                work(idx)
            except BaseException as e:  # noqa: BLE001
                failures.append(e)

        threads = [threading.Thread(target=wrapped, args=(i,))
                   for i in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(failures, [], f"Exceptions in worker threads: {failures}")

    def test_shared_parent(self):
        """Insert and remove children on the same parent from every thread."""
        parent = ObjectType()

        def work(idx):
            for _ in range(ITERS):
                child = ObjectType()
                child.setParent(parent)
                parent.children()
                parent.takeChild(child)
                Shiboken.delete(child)

        self.spin(work)

    def test_destroy_race(self):
        """Destroy parents that still own a child."""
        def work(idx):
            for _ in range(ITERS):
                parent = ObjectType()
                child = ObjectType()
                child.setParent(parent)
                Shiboken.delete(parent)

        self.spin(work)

    def test_reparent(self):
        """Move children between two shared parents."""
        first, second = ObjectType(), ObjectType()

        def work(idx):
            for _ in range(ITERS):
                child = ObjectType()
                child.setParent(first)
                child.setParent(second)
                second.takeChild(child)
                Shiboken.delete(child)

        self.spin(work)

    def test_shared_delete(self):
        """Race to destroy the same wrappers.

        Deleting an already invalidated wrapper must be a safe no-op, and two
        threads doing it at once must not double free.
        """
        pool_size = 400
        pool = [ObjectType() for _ in range(pool_size)]
        lock = threading.Lock()

        def work(idx):
            for i in range(ITERS):
                slot = (i * 7 + idx) % pool_size
                Shiboken.delete(pool[slot])
                if idx == 0:  # one thread refills, racing the deleters
                    with lock:
                        pool[slot] = ObjectType()

        self.spin(work)


if __name__ == "__main__":
    unittest.main()
