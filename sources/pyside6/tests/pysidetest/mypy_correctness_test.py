# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
import unittest
import subprocess
import time

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

try:
    import mypy     # noqa: F401
    HAVE_MYPY = True
except ModuleNotFoundError:
    HAVE_MYPY = False

import PySide6
from PySide6 import SKIP_MYPY_TEST


@unittest.skipIf(not HAVE_MYPY, "The mypy test was skipped because mypy is not installed")
@unittest.skipIf(SKIP_MYPY_TEST, "The mypy test was disabled")
class MypyCorrectnessTest(unittest.TestCase):

    def setUp(self):
        self.pyside_dir = Path(PySide6.__file__).parent
        self.build_dir = self.pyside_dir.parent.parent
        os.chdir(self.build_dir)

    def testMypy(self):
        cmd = [sys.executable, "-m", "mypy", f"{os.fspath(self.pyside_dir)}"]
        time_pre = time.time()
        ret = subprocess.run(cmd, capture_output=True)
        time_post = time.time()
        for line in ret.stdout.decode("utf-8").split("\n"):
            print(line)
        print(f"Time used for mypy test = {(time_post - time_pre):.5} s")
        self.assertEqual(ret.returncode, 0)


if __name__ == '__main__':
    unittest.main()
