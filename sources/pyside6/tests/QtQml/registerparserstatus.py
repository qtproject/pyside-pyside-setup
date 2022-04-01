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

from PySide6.QtCore import (QCoreApplication, QUrl)
from PySide6.QtQml import (QQmlComponent, QQmlEngine,
                           QmlElement, QPyQmlParserStatus)


QML_IMPORT_NAME = "ParserStatus"
QML_IMPORT_MAJOR_VERSION = 1


def component_error(component):
    result = ""
    for e in component.errors():
        if result:
            result += "\n"
        result += str(e)
    return result


@QmlElement
class TestItem(QPyQmlParserStatus):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.component_complete_called = False
        self.class_begin_called = False

    def componentComplete(self):
        self.component_complete_called = True

    def classBegin(self):
        self.class_begin_called = True


class TestQmlAttached(unittest.TestCase):
    def testIt(self):
        app = QCoreApplication(sys.argv)
        file = Path(__file__).resolve().parent / 'registerparserstatus.qml'
        url = QUrl.fromLocalFile(file)
        engine = QQmlEngine()
        component = QQmlComponent(engine, url)
        item = component.create()
        self.assertTrue(item, component_error(component))
        self.assertTrue(item.component_complete_called)
        self.assertTrue(item.class_begin_called)


if __name__ == '__main__':
    unittest.main()
