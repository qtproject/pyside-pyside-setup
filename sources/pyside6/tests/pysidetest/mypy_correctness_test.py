# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import re
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

qtest_env = os.environ.get("QTEST_ENVIRONMENT", "")
is_ci = qtest_env == "ci"
# When we are in COIN, we enforce mypy existence, to prevent misconfigurations.
USE_MYPY = True if is_ci else HAVE_MYPY


def dump_erroneous_pyi_files(err_lines, pyi_dir):
    seen = set()
    for err_line in err_lines:
        if match := re.search(r"Qt\w+\.pyi", err_line):
            if (pyi := match.group(0)) not in seen:
                seen.add(pyi)
                print(f"----- dump of {pyi} -----")
                with open(Path(pyi_dir) / pyi) as f:
                    line_no = 0
                    for line in f:
                        line_no += 1
                        print(f"{pyi}:{line_no} {line.rstrip()}")
                print()


@unittest.skipIf(not USE_MYPY, "The mypy test was skipped because mypy is not installed")
@unittest.skipIf(SKIP_MYPY_TEST, "The mypy test was disabled")
class MypyCorrectnessTest(unittest.TestCase):

    def setUp(self):
        self.pyside_dir = Path(PySide6.__file__).parent
        self.build_dir = self.pyside_dir.parent.parent
        os.chdir(self.build_dir)
        self.project_dir = Path(__file__).resolve().parents[4]
        # For safety about future changes, check that we are sitting above the sources dir.
        self.assertTrue((self.project_dir / "sources").exists())
        # Check if the project dir can be written. If so, put the mypy cache there.
        test_fname = self.project_dir / ".tmp test writable"
        try:
            with test_fname.open("w") as f:
                f.write("works!")
                f.close()
                test_fname.unlink()
            self.cache_dir = self.project_dir / f".pyside{PySide6.__version__}_mypy_cache"
        except Exception:
            self.cache_dir = ".mypy_cache"  # This is the mypy default.

    def testMypy(self):
        self.assertTrue(HAVE_MYPY)
        insert_version = ["--python-version", "3.11"] if sys.version_info[:2] < (3, 11) else []
        cmd = ([sys.executable, "-m", "mypy", "--pretty", "--cache-dir", self.cache_dir]
               + insert_version + [self.pyside_dir])
        time_pre = time.time()
        ret = subprocess.run(cmd, capture_output=True)
        time_post = time.time()
        err_lines = ret.stdout.decode("utf-8").split("\n")
        for line in err_lines:
            print(line)
        print(f"Time used for mypy test = {(time_post - time_pre):.5} s")
        if ret.returncode != 0:
            dump_erroneous_pyi_files(err_lines, self.pyside_dir)
        self.assertEqual(ret.returncode, 0)


if __name__ == '__main__':
    unittest.main()
