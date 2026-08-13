# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import subprocess
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6


# Note:
# "from PySide6 import *" can only be used at module level.
# It is also really not recommended to use. But for testing,
# the "__all__" variable is a great feature!
class AllModulesImportTest(unittest.TestCase):
    def testAllModulesCanImport(self):
        # would also work: exec("from PySide6 import *")
        for name in PySide6.__all__:
            exec(f"import PySide6.{name}")

    @unittest.skipUnless(hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled(),
                         "Only for GIL disabled builds.")
    def testNoModuleTurnsTheGilBackOn(self):
        """A module whose type system forgets module-uses-gil="false" declares
        that it needs the GIL, and importing it switches the GIL back on for
        the whole process - silently undoing free threading for everyone.

        Runs in a subprocess: the other tests here import every module, and one
        of them turns the GIL on, which cannot be undone within the process."""
        proc = subprocess.run([sys.executable, __file__, "--check-gil"],
                              capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def testAllReappearsAfterDel(self):
        # This is the only incompatibility that remains:
        # After __all__ is deleted, it will re-appear.
        PySide6.__all__ = 42
        self.assertEqual(PySide6.__dict__["__all__"], 42)
        del PySide6.__all__
        self.assertTrue(PySide6.__dict__["__all__"])
        self.assertNotEqual(PySide6.__dict__["__all__"], 42)


def _check_gil_stays_off():
    """Import every module and report the first one that turns the GIL on."""
    # QtQmlFeatures declares Py_MOD_GIL_USED by hand. It is not generated, so
    # the type system default does not reach it; left to its authors to decide.
    for name in (n for n in PySide6.__all__ if n != "QtQmlFeatures"):
        try:
            exec(f"import PySide6.{name}")
        except ImportError:
            continue  # module not built
        if sys._is_gil_enabled():
            print(f"importing PySide6.{name} re-enabled the GIL")
            return 1
    return 0


if __name__ == '__main__':
    if "--check-gil" in sys.argv:
        sys.exit(_check_gil_stays_off())
    unittest.main()
