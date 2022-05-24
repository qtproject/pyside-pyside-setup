# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionViewItem


class Properties(unittest.TestCase):

    def testStaticProperty(self):
        self.assertEqual(QGraphicsItem.UserType, 65536)

    def testInstanceProperty(self):
        p = QStyleOptionViewItem()
        self.assertTrue(isinstance(p.locale, QLocale))

        # PSYIDE-304, can assign to a "const QWidget *" field
        p.widget = None


if __name__ == '__main__':
    unittest.main()
