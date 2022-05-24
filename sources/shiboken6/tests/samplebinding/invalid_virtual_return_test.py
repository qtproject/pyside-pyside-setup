#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for returning invalid types in a virtual function'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import ObjectModel, ObjectType, ObjectView

import warnings


class MyObject(ObjectType):
    pass


class ListModelWrong(ObjectModel):

    def __init__(self, parent=None):
        ObjectModel.__init__(self, parent)
        self.obj = 0

    def data(self):
        warnings.simplefilter('error')
        # Shouldn't segfault. Must set TypeError
        return self.obj


class ModelWrongReturnTest(unittest.TestCase):

    def testWrongTypeReturn(self):
        model = ListModelWrong()
        view = ObjectView(model)
        self.assertRaises(RuntimeWarning, view.getRawModelData) # calls model.data()


if __name__ == '__main__':
    unittest.main()
