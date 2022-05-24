#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtWidgets import QTableView


class TestModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

    def rowCount(self, parent):
        return 0

    def columnCount(self, parent):
        return 0

    def data(self, index, role):
        return None


class KeepReferenceTest(UsesQApplication):

    def testModelWithoutParent(self):
        view = QTableView()
        model = TestModel()
        view.setModel(model)
        samemodel = view.model()
        self.assertEqual(model, samemodel)

    def testModelWithParent(self):
        view = QTableView()
        model = TestModel(None)
        view.setModel(model)
        samemodel = view.model()
        self.assertEqual(model, samemodel)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReferenceCounting(self):
        '''Tests reference count of model object referred by view objects.'''
        model1 = TestModel()
        refcount1 = sys.getrefcount(model1)
        view1 = QTableView()
        view1.setModel(model1)
        self.assertEqual(sys.getrefcount(view1.model()), refcount1 + 1)

        view2 = QTableView()
        view2.setModel(model1)
        self.assertEqual(sys.getrefcount(view2.model()), refcount1 + 2)

        model2 = TestModel()
        view2.setModel(model2)
        self.assertEqual(sys.getrefcount(view1.model()), refcount1 + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReferenceCountingWhenDeletingReferrer(self):
        '''Tests reference count of model object referred by deceased view object.'''
        model = TestModel()
        refcount1 = sys.getrefcount(model)
        view = QTableView()
        view.setModel(model)
        self.assertEqual(sys.getrefcount(view.model()), refcount1 + 1)

        del view
        self.assertEqual(sys.getrefcount(model), refcount1)

    def testReferreedObjectSurvivalAfterContextEnd(self):
        '''Model object assigned to a view object must survive after getting out of context.'''
        def createModelAndSetToView(view):
            model = TestModel()
            model.setObjectName('created model')
            view.setModel(model)
        view = QTableView()
        createModelAndSetToView(view)
        model = view.model()


if __name__ == '__main__':
    unittest.main()

