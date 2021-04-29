#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
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

from PySide6.QtCore import Property, Signal, QTimer, QUrl, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlRegisterSingletonType
from PySide6.QtQuick import QQuickView

finalResult = 0


class SingletonQObject(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._data = 100

    def getData(self):
        return self._data

    def setData(self, data):
        global finalResult
        finalResult = self._data = data

    data = Property(int, getData, setData)


def singletonQObjectCallback(engine):
    obj = SingletonQObject()
    obj.setData(50)
    return obj


def singletonQJSValueCallback(engine):
    return engine.evaluate("new Object({data: 50})")


class TestQmlSupport(unittest.TestCase):
    def testIt(self):
        app = QGuiApplication([])

        qmlRegisterSingletonType(SingletonQObject, 'Singletons', 1, 0, 'SingletonQObjectNoCallback')
        qmlRegisterSingletonType(SingletonQObject, 'Singletons', 1, 0, 'SingletonQObjectCallback',
                                 singletonQObjectCallback)

        qmlRegisterSingletonType('Singletons', 1, 0, 'SingletonQJSValue', singletonQJSValueCallback)

        view = QQuickView()
        file = Path(__file__).resolve().parent / 'registersingletontype.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(os.fspath(file)))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()
        QTimer.singleShot(250, view.close)
        app.exec_()
        self.assertEqual(finalResult, 200)


if __name__ == '__main__':
    unittest.main()
