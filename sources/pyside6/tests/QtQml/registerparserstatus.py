# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
