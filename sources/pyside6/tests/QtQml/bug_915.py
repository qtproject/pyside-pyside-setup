#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtQuick import QQuickView, QQuickItem


class TestBug915(TimedQGuiApplication):
    def testReturnPolicy(self):
        view = QQuickView()

        item1 = QQuickItem()
        item1.setObjectName("Item1")
        item1.setParentItem(view.contentItem())
        self.assertEqual(item1.objectName(), "Item1")  # check if the item still valid

        item2 = QQuickItem()
        item2.setObjectName("Item2")
        item2.setParentItem(view.contentItem())
        item1 = None
        self.assertEqual(item2.objectName(), "Item2")  # check if the item still valid

        view = None


if __name__ == '__main__':
    unittest.main()


