# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

"""Incarnate the lazy types of a module from several threads at once.

Types are created on first attribute access, from whichever thread gets there
first (PYSIDE-2404). Without serialization two threads can run the same
creation function at the same time, because the name stays in the creation map
until it returns; one of them then works with a half-built type and the
process dies. Qt reaches this through its own worker threads - the QML loader
calling a Python network factory was the first case seen - but the window is
reachable from plain Python, which is what this test does.

Clear the LazyTypeLock bit of PYSIDE6_OPTION_FT and this test segfaults;
that is what makes it a test.
"""

import os
import random
import sys
import sysconfig
import threading
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

MSG_SKIP = "Only for GIL disabled builds."

THREADS = 8
ROUNDS = 3


def is_gil_disabled():
    gil_disabled_build = sysconfig.get_config_vars('Py_GIL_DISABLED')[0]
    return gil_disabled_build and not sys._is_gil_enabled()


@unittest.skipUnless(is_gil_disabled(), MSG_SKIP)
class LazyTypeRaceTest(unittest.TestCase):

    def testConcurrentIncarnation(self):
        # Not QtCore: init_test_paths() has already touched it. dir() lists
        # the lazy names without creating them, getattr() creates them.
        import PySide6.QtGui as module
        names = [name for name in dir(module) if name[0].isupper()]
        self.assertGreater(len(names), 50)

        start = threading.Barrier(THREADS)
        failures = []

        def worker(seed):
            order = names[:]
            random.Random(seed).shuffle(order)
            try:
                start.wait()
                for _ in range(ROUNDS):
                    for name in order:
                        getattr(module, name)
            except Exception as e:
                failures.append(e)

        threads = [threading.Thread(target=worker, args=(seed,))
                   for seed in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(failures, [])
        # Every name resolves to the same object for everyone afterwards.
        for name in names:
            self.assertIs(getattr(module, name), getattr(module, name))


if __name__ == '__main__':
    unittest.main()
