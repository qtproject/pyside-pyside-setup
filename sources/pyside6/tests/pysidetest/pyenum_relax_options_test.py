#!/usr/bin/python
#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
PYSIDE-1735: Testing different relax options for Enums

This test uses different configurations and initializes QtCore with it.
Because re-initialization is not possible, the test uses a subprocess
for it. This makes the test pretty slow.

Maybe we should implement a way to re-initialize QtCore enums without
using subprocess, just to speed this up??
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import subprocess
import tempfile
from textwrap import dedent


def runtest(program):
    passed_path = os.fspath(Path(__file__).resolve().parents[1])
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as fp:
        preamble = dedent(f"""
            import os
            import sys
            from pathlib import Path
            sys.path.append({passed_path!r})
            from init_paths import init_test_paths
            init_test_paths(False)
            """)
        print(preamble, program, file=fp)
        fp.close()
        try:
            subprocess.run([sys.executable, fp.name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"\ninfo: {e.__class__.__name__}: {e.stderr}")
            return False
        finally:
            os.unlink(fp.name)

def testprog2(option):
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        from enum import IntEnum
        assert(issubclass(QtCore.Qt.DateFormat, IntEnum))
        """))

def testprog4(option):
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        QtCore.QtDebugMsg
        """))

def testprog8_16(option):
    # this test needs flag 16, or the effect would be hidden by forgiving mode
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        QtCore.Qt.AlignTop
        """))

def testprog32(option):
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        QtCore.Qt.Alignment
        """))

def testprog64(option):
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        QtCore.Qt.AlignmentFlag()
        """))

def testprog128(option):
    return runtest(dedent(f"""
        sys.pyside63_option_python_enum = {option}
        from PySide6 import QtCore
        QtCore.Qt.Key(1234567)
        """))


class TestPyEnumRelaxOption(unittest.TestCase):
    """
    This test is a bit involved, because we cannot unload QtCore after it is loaded once.
    We use subprocess to test different cases, anyway.
    """

    def test_enumIsIntEnum(self):
        self.assertTrue(testprog2(2))
        self.assertFalse(testprog2(4))

    def test_globalDefault(self):
        self.assertTrue(testprog4(4))
        self.assertFalse(testprog4(1))
        self.assertTrue(testprog4(12))

    def test_localDefault(self):
        self.assertTrue(testprog8_16(8+16))
        self.assertFalse(testprog8_16(0+16))

    def test_fakeRenames(self):
        self.assertTrue(testprog32(1))
        self.assertFalse(testprog32(32))

    def test_zeroDefault(self):
        self.assertTrue(testprog64(1))
        self.assertFalse(testprog64(64))

    def test_Missing(self):
        self.assertTrue(testprog128(1))
        self.assertFalse(testprog128(128))


if __name__ == "__main__":
    unittest.main()
