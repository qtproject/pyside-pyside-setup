# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import subprocess
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)


def run_scenario():
    """Deterministic lock inversion between a Python lock and the binding lock.

    thread A: holds a threading.Lock, then calls a generated method
    thread B: enters the binding through setParent (not allow-thread), which
              delivers childEvent to a Python override that wants A's lock

    On a free-threaded build with a binding lock held across the Python
    callback this is an AB-BA deadlock. No binding lock is held across the
    callback - the state lock covers a short transaction and is released
    before anything calls into Python - so both threads must complete. On GIL
    builds the scenario is trivially safe.
    """
    import threading

    from PySide6.QtCore import QObject, QCoreApplication

    app = QCoreApplication([])  # noqa: F841 childEvent needs event delivery

    pylock = threading.Lock()
    a_has_pylock = threading.Event()
    b_in_python = threading.Event()
    done = []

    class Parent(QObject):
        def childEvent(self, event):
            b_in_python.set()
            with pylock:
                pass

    parent = Parent()
    child = QObject()
    other = QObject()

    def thread_a():
        with pylock:
            a_has_pylock.set()
            b_in_python.wait(timeout=10)
            other.setObjectName("unrelated")
            done.append("A")

    def thread_b():
        a_has_pylock.wait(timeout=10)
        child.setParent(parent)
        done.append("B")

    ta = threading.Thread(target=thread_a, daemon=True)
    tb = threading.Thread(target=thread_b, daemon=True)
    ta.start()
    tb.start()
    ta.join(timeout=30)
    tb.join(timeout=30)

    if len(done) == 2:
        return 0
    print(f"DEADLOCK: completed={done} A_alive={ta.is_alive()} "
          f"B_alive={tb.is_alive()}", file=sys.stderr, flush=True)
    # A deadlocked thread inside the binding prevents a clean interpreter
    # shutdown; report and leave hard.
    os._exit(1)


class LockInversionTest(unittest.TestCase):
    """The scenario runs in a subprocess with a hard timeout, so a regression
    fails the test instead of hanging the suite."""

    def test_no_deadlock(self):
        cmd = [sys.executable, __file__, "--child"]
        proc = subprocess.run(cmd, timeout=120)
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    if "--child" in sys.argv:
        sys.exit(run_scenario())
    unittest.main()
