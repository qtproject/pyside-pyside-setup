#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QPasswordDigestor'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QCryptographicHash
from PySide6.QtNetwork import QPasswordDigestor


class TestPasswordDigestor(unittest.TestCase):
    def test(self):
        b = QPasswordDigestor.deriveKeyPbkdf1(QCryptographicHash.Sha1,
                                              b'test', b'saltnpep', 10, 20)
        self.assertEqual(b.size(), 20)


if __name__ == '__main__':
    unittest.main()
