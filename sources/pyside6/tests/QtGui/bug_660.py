# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QStandardItemModel, QStandardItem


class MyItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.appendRow([QStandardItem('Item 1'),])

    def mimeTypes(self):
        mtypes = super(MyItemModel, self).mimeTypes()
        mtypes.append('application/my-form')
        return mtypes

    def mimeData(self, indexes):
        self.__mimedata = super(MyItemModel, self).mimeData(indexes)
        self.__mimedata.setData('application/my-form', bytes('hi', "UTF-8"))
        return self.__mimedata


class TestBug660(unittest.TestCase):
    '''QMimeData type deleted prematurely when overriding mime-type in QStandardItemModel drag and drop'''
    def testIt(self):
        model = MyItemModel()
        model.mimeData([model.index(0, 0)])  # if it doesn't raise an exception it's all right!


if __name__ == '__main__':
    unittest.main()
