#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# Copyright (C) 2011 Thomas Perl <m@thp.io>
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Test case for PySide bug 814
# http://bugs.pyside.org/show_bug.cgi?id=814
# archive:
# https://srinikom.github.io/pyside-bz-archive/814.html
# 2011-04-08 Thomas Perl <m@thp.io>
# Released under the same terms as PySide itself

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtCore import QUrl, QAbstractListModel, QModelIndex, Qt
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "test.ListModel"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()

    def roleNames(self):
        return { Qt.DisplayRole: b'pysideModelData' }

    def rowCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return 'blubb'
        return None


class TestBug814(TimedQGuiApplication):
    def testAbstractItemModelTransferToQML(self):
        view = QQuickView()
        model = ListModel()
        view.setInitialProperties({"pythonModel": model})
        file = Path(__file__).resolve().parent / 'bug_814.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        view.show()


if __name__ == '__main__':
    unittest.main()

