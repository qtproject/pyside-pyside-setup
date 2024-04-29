# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from helper.usesqapplication import UsesQApplication  # noqa: E402, F401

from PySide6.QtCore import QObject, QUrl, Property, qInstallMessageHandler  # noqa: E402
from PySide6.QtQml import ListProperty, QmlElement  # noqa: E402
from PySide6.QtQuick import QQuickView  # noqa: E402


QML_IMPORT_NAME = "test.ListPropertyTest"
QML_IMPORT_MAJOR_VERSION = 1

output_messages = []


def message_handler(mode, context, message):
    global output_messages
    output_messages.append(f"{message}")


class InheritsQObject(QObject):
    pass


def dummyFunc():
    pass


@QmlElement
class Person(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self._name = ''
        self._friends = []

    def appendFriend(self, friend):
        self._friends.append(friend)

    def friendCount(self):
        return len(self._friends)

    def friend(self, index):
        return self._friends[index]

    def removeLastItem(self):
        if len(self._friends) > 0:
            self._friends.pop()

    def replace(self, index, friend):
        if 0 <= index < len(self._friends):
            self._friends[index] = friend

    def clear(self):
        self._friends.clear()

    @Property(str, final=True)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    friends = ListProperty(QObject, append=appendFriend, count=friendCount, at=friend,
                           removeLast=removeLastItem, replace=replace, clear=clear)


class TestListProperty(UsesQApplication):
    def testIt(self):

        # Verify that type checking works properly
        type_check_error = False

        try:
            ListProperty(QObject)
            ListProperty(InheritsQObject)
        except Exception:
            type_check_error = True

        self.assertFalse(type_check_error)

        try:
            ListProperty(int)
        except TypeError:
            type_check_error = True

        self.assertTrue(type_check_error)

        # Verify that method validation works properly
        method_check_error = False

        try:
            ListProperty(QObject, append=None, at=None, count=None, replace=None, clear=None,
                         removeLast=None)  # Explicitly setting None
            ListProperty(QObject, append=dummyFunc)
            ListProperty(QObject, count=dummyFunc, at=dummyFunc)
        except Exception:
            method_check_error = True

        self.assertFalse(method_check_error)

        try:
            ListProperty(QObject, append=QObject())
        except Exception:
            method_check_error = True

        self.assertTrue(method_check_error)

    def testListPropParameters(self):
        global output_messages
        qInstallMessageHandler(message_handler)
        view = QQuickView()
        file = Path(__file__).resolve().parent / 'listproperty.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        view.show()
        self.assertEqual(output_messages[0], "List length: 3")
        self.assertEqual(output_messages[1], "First element: Alice")
        self.assertEqual(output_messages[2], "Removing last item: Charlie")
        self.assertEqual(output_messages[3], "Replacing last item: Bob")
        self.assertEqual(output_messages[4], "Replaced last item: David")
        self.assertEqual(output_messages[5], "List length after clearing: 0")


if __name__ == '__main__':
    unittest.main()
