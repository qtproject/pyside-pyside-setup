# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''(Very) Simple test case for missing names from QtGui and QtWidgets'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6 import QtGui
from PySide6 import QtWidgets


class MissingClasses(unittest.TestCase):
    def testQDrag(self):  # Bug 222
        getattr(QtGui, 'QDrag')

    def testQDropEvent(self):  # Bug 255
        getattr(QtGui, 'QDropEvent')


class MissingMembers(unittest.TestCase):

    def testQFontMetricsSize(self):  # Bug 223
        QtGui.QFontMetrics.size

    def testQLayoutSetSpacing(self):  # Bug 231
        QtWidgets.QLayout.setSpacing

    def testQImageLoad(self):  # Bug 257
        QtGui.QImage.load

    def testQStandardItemModelinsertRow(self):  # Bug 227
        QtGui.QStandardItemModel.insertRow


if __name__ == '__main__':
    unittest.main()
