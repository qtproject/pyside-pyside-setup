# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import sysconfig
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject, QCoreApplication, QThread, QThreadPool, QRunnable


MSG_SKIP = "Only for GIL disabled builds."


def is_gil_disabled():
    gil_disabled_build = sysconfig.get_config_vars('Py_GIL_DISABLED')[0]
    return gil_disabled_build and not sys._is_gil_enabled()


class Task(QRunnable):
    exceptions = []

    def run(self):
        try:
            obj = QObject()
            obj.moveToThread(QThread.currentThread())  # Ensure thread affinity
        except Exception as e:
            self.exceptions.append(e)
            raise  # Force exception to propagate


class ThreadPoolTest(unittest.TestCase):
    """Stress test for disable GIL."""

    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication(sys.argv)

    @unittest.skipUnless(is_gil_disabled(), MSG_SKIP)
    def test_threadpool_stress(self):
        """Force crashes by handling more threads using QThreadPool"""
        pool = QThreadPool.globalInstance()
        exceptions = []

        # Submit a large number of tasks to QThreadPool
        for _ in range(500):  # Huge number of tasks to stress the thread pool
            pool.start(Task())

        exceptions = Task.exceptions
        self.assertTrue(pool.waitForDone())  # Wait for all tasks to finish

        self.assertEqual(len(exceptions), 0, f"Exceptions during QThreadPool tasks: {exceptions}")


if __name__ == "__main__":
    unittest.main()
