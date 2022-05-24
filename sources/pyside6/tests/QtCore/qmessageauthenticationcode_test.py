#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QMessageAuthenticationCode'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCryptographicHash, QMessageAuthenticationCode


class TestQMessageAuthenticationCode (unittest.TestCase):
    def test(self):
        code = QMessageAuthenticationCode(QCryptographicHash.Sha1, bytes('bla', "UTF-8"))
        result = code.result()
        self.assertTrue(result.size() > 0)
        print(result.toHex())


if __name__ == '__main__':
    unittest.main()
