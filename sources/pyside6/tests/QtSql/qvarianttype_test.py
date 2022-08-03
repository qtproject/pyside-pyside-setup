# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QVariant::Type converter'''
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QMetaType
from PySide6.QtSql import QSqlField


class QVariantTypeTest(unittest.TestCase):
    def testQVariantType(self):
        new_enum = sys.pyside63_option_python_enum
        cmp_id = QMetaType.QString.value if new_enum else QMetaType.QString

        f = QSqlField("name", QMetaType(QMetaType.QString))
        self.assertEqual(f.metaType().id(), cmp_id)

        f = QSqlField("name", QMetaType.fromName(b"QString"))
        self.assertEqual(f.metaType().id(), cmp_id)

        f = QSqlField("name", QMetaType.fromName(b"double"))
        self.assertEqual(f.metaType(), float)

        f = QSqlField("name", float)
        self.assertEqual(f.metaType(), float)

        f = QSqlField("name", int)
        self.assertEqual(f.metaType(), int)


if __name__ == '__main__':
    unittest.main()
