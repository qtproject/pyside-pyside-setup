#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

'''Unit tests for QSharedMemory'''

import ctypes
import os
import subprocess
import sys
import unittest

from pathlib import Path
FILE = Path(__file__).resolve()
sys.path.append(os.fspath(FILE.parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QSharedMemory, QRandomGenerator, qVersion
from qsharedmemory_client import read_string


TEST_STRING = 'ABCD'


def run(cmd):
    # FIXME Python 3.7: Use subprocess.run()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False,
                            universal_newlines=True)
    output, error = proc.communicate()
    proc.wait()
    return_code = proc.returncode
    return (return_code, output, error)


class QSharedMemoryTest(unittest.TestCase):

    def setUp(self):
        r = QRandomGenerator.global_().bounded(1000)
        v = qVersion()
        self._name = f"pyside{v}_test_{r}"
        print(self._name)
        self._shared_memory = QSharedMemory(self._name)

    def tearDown(self):
        if self._shared_memory.isAttached():
            self._shared_memory.detach()

    def test(self):
        # Create and write
        self.assertTrue(self._shared_memory.create(1024, QSharedMemory.ReadWrite))
        self.assertTrue(self._shared_memory.lock())
        mv = memoryview(self._shared_memory.data())
        for idx, c in enumerate(TEST_STRING + chr(0)):
            mv[idx] = ord(c)
        mv = None
        self.assertTrue(self._shared_memory.unlock())

        # Read
        self.assertTrue(self._shared_memory.lock())
        self.assertEqual(read_string(self._shared_memory), TEST_STRING)
        self.assertTrue(self._shared_memory.unlock())

        # Run a subprocess and let it read
        client = FILE.parent / 'qsharedmemory_client.py'
        returncode, output, error = run([sys.executable, client, self._name])
        if error:
            print(error, file=sys.stderr)
        self.assertEqual(returncode, 0)
        self.assertEqual(output, TEST_STRING)


if __name__ == '__main__':
    unittest.main()
