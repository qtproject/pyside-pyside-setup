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

'''
Test bug 451: http://bugs.openbossa.org/show_bug.cgi?id=451

An archive of said bug:
https://srinikom.github.io/pyside-bz-archive/451.html
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring

from PySide6.QtCore import QObject, QUrl, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView


class PythonObject(QObject):
    def __init__(self):
        super().__init__(None)
        self._called = ""
        self._arg1 = None
        self._arg2 = None

    def setCalled(self, v):
        self._called = v

    def setArg1(self, v):
        self._arg1 = v

    def setArg2(self, v):
        self._arg2 = v

    def getCalled(self):
        return self._called

    def getArg1(self):
        return self._arg1

    def getArg2(self):
        return self._arg2

    called = Property(str, getCalled, setCalled)
    arg1 = Property(int, getArg1, setArg1)
    arg2 = Property('QVariant', getArg2, setArg2)

class TestBug(unittest.TestCase):
    def testQMLFunctionCall(self):
        app = QGuiApplication(sys.argv)
        view = QQuickView()

        obj = PythonObject()
        context = view.rootContext()
        context.setContextProperty("python", obj)
        file = Path(__file__).resolve().parent / 'bug_451.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(os.fspath(file)))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        root.simpleFunction()
        self.assertEqual(obj.called, "simpleFunction")

        root.oneArgFunction(42)
        self.assertEqual(obj.called, "oneArgFunction")
        self.assertEqual(obj.arg1, 42)

        root.twoArgFunction(10, app)
        self.assertEqual(obj.called, "twoArgFunction")
        self.assertEqual(obj.arg1, 10)
        self.assertEqual(obj.arg2, app)

        rvalue = root.returnFunction()
        self.assertEqual(obj.called, "returnFunction")
        self.assertEqual(rvalue, 42)


if __name__ == '__main__':
    unittest.main()
