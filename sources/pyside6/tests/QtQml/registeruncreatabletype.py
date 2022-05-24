# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import qmlcomponent_errorstring

from PySide6.QtCore import Property, QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QmlUncreatable, QQmlEngine, QQmlComponent

noCreationReason = 'Cannot create an item of type: Uncreatable (expected)'

QML_IMPORT_NAME = "Charts"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlUncreatable(noCreationReason)
class Uncreatable(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._name = 'uncreatable'

    def getName(self):
        return self._name

    def setName(self, value):
        self._name = value

    name = Property(str, getName, setName)


class TestQmlSupport(unittest.TestCase):

    def testIt(self):
        app = QGuiApplication([])

        engine = QQmlEngine()
        file = Path(__file__).resolve().parent / 'registeruncreatable.qml'
        self.assertTrue(file.is_file())
        component = QQmlComponent(engine, QUrl.fromLocalFile(file))

        # Check that the uncreatable item produces the correct error
        self.assertEqual(component.status(), QQmlComponent.Error)
        errorFound = False
        for e in component.errors():
            if noCreationReason in e.toString():
                errorFound = True
                break
        self.assertTrue(errorFound)


if __name__ == '__main__':
    unittest.main()
