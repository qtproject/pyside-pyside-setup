#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
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

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication
from PySide6.QtCore import QObject, QTimer, QUrl, Property, Slot
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "test.RotateValue"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RotateValue(QObject):
    def __init__(self):
        super().__init__()

    @Slot(result=int)
    def val(self):
        return 100

    def setRotation(self, v):
        self._rotation = v

    def getRotation(self):
        return self._rotation

    rotation = Property(int, getRotation, setRotation)


class TestConnectionWithInvalidSignature(TimedQGuiApplication):

    def testSlotRetur(self):
        view = QQuickView()
        rotatevalue = RotateValue()

        timer = QTimer()
        timer.start(2000)

        view.setInitialProperties({"rotatevalue": rotatevalue})
        file = Path(__file__).resolve().parent / 'bug_456.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        button = root.findChild(QObject, "buttonMouseArea")
        view.show()
        button.entered.emit()
        self.assertEqual(rotatevalue.rotation, 100)


if __name__ == '__main__':
    unittest.main()
