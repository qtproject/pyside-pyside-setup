#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
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

from helper.helper import qmlcomponent_errorstring
from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtCore import Property, QObject, QUrl, qVersion
from PySide6.QtGui import QGuiApplication, QRasterWindow
from PySide6.QtQml import (QmlNamedElement, QmlForeign, QQmlEngine,
                           QQmlComponent)


"""Test the QmlForeign decorator, letting the QQmlEngine create a QRasterWindow."""


QML_IMPORT_NAME = "Foreign"
QML_IMPORT_MAJOR_VERSION = 1


@QmlNamedElement("QRasterWindow")
@QmlForeign(QRasterWindow)
class RasterWindowForeign(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestQmlForeign(TimedQGuiApplication):

    def testIt(self):
        engine = QQmlEngine()
        file = Path(__file__).resolve().parent / 'registerforeign.qml'
        self.assertTrue(file.is_file())
        component = QQmlComponent(engine, QUrl.fromLocalFile(file))
        window = component.create()
        self.assertTrue(window, qmlcomponent_errorstring(component))
        self.assertEqual(type(window), QRasterWindow)
        window.setTitle(f"Qt {qVersion()}")
        window.show()
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
