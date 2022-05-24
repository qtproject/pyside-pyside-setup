#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QJsonDocument/nullptr_t'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QJsonDocument


class QJsonDocumentTest(unittest.TestCase):

    def testToVariant(self):
        a = QJsonDocument.fromJson(b'{"test": null}')
        self.assertIsInstance(a, QJsonDocument)
        self.assertEqual(str(a.toVariant()), "{'test': None}")

        b = QJsonDocument.fromJson(b'{"test": [null]}')
        self.assertIsInstance(b, QJsonDocument)
        self.assertEqual(str(b.toVariant()), "{'test': [None]}")


if __name__ == '__main__':
    unittest.main()
