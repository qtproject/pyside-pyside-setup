# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QCoreApplication, QUrl, QObject, Property)
from PySide6.QtQml import (QQmlComponent, QQmlEngine, QmlAnonymous,
                           QmlAttached, QmlElement, ListProperty,
                           qmlAttachedPropertiesObject)


QML_IMPORT_NAME = "TestLayouts"
QML_IMPORT_MAJOR_VERSION = 1


EXPECTED_MARGINS = [10, 20]


def component_error(component):
    result = ""
    for e in component.errors():
        if result:
            result += "\n"
        result += str(e)
    return result


@QmlAnonymous
class TestLayoutAttached(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._leftMargin = 0

    @Property(int)
    def leftMargin(self):
        return self._leftMargin

    @leftMargin.setter
    def leftMargin(self, m):
        self._leftMargin = m


@QmlElement
class TestWidget(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)


@QmlElement
@QmlAttached(TestLayoutAttached)
class TestLayout(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._widgets = []

    def widget(self, n):
        return self._widgets[n]

    def widgetCount(self):
        return len(self._widgets)

    def addWidget(self, w):
        self._widgets.append(w)

    @staticmethod
    def qmlAttachedProperties(self, o):
        return TestLayoutAttached(o)

    widgets = ListProperty(TestWidget, addWidget)


class TestQmlAttached(unittest.TestCase):
    def testIt(self):
        app = QCoreApplication(sys.argv)
        file = Path(__file__).resolve().parent / 'registerattached.qml'
        url = QUrl.fromLocalFile(file)
        engine = QQmlEngine()
        component = QQmlComponent(engine, url)
        layout = component.create()
        self.assertTrue(layout, component_error(component))

        actual_margins = []
        for i in range(layout.widgetCount()):
            w = layout.widget(i)
            a = qmlAttachedPropertiesObject(TestLayout, w, False)
            actual_margins.append(a.leftMargin)
        self.assertEqual(EXPECTED_MARGINS, actual_margins)


if __name__ == '__main__':
    unittest.main()
