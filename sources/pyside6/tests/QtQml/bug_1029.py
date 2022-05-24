# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickView, QQuickItem


def register_qml_types():
    class TestClass(QQuickItem):
        def __init__(self, parent=None):
            QQuickItem.__init__(self, parent)

    qmlRegisterType(TestClass, "UserTypes", 1, 0, "TestClass")


def main():
    app = QGuiApplication([])

    # reg qml types here
    register_qml_types()

    # force gc to run
    gc.collect()

    view = QQuickView()
    url = QUrl(__file__.replace(".py", ".qml"))
    view.setSource(url)


if __name__ == "__main__":
    main()
