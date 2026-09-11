#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Tests what an invalidation walk may and may not reach through a reference.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import shiboken6 as Shiboken
from sample import ObjectModel, ObjectType, ObjectView


class InvalidateReferredTest(unittest.TestCase):
    '''An invalidated holder takes its children with it, not what it refers to.'''

    def testReferredObjectSurvivesItsHolder(self):
        '''A child dies with its parent, a referred object does not.'''
        # All three come from C++: an object constructed in Python carries a
        # C++ wrapper, and invalidation never marks those - the difference
        # would not be visible.
        parent = ObjectType.create()
        view = ObjectView.create()
        view.setParent(parent)
        model = ObjectModel.create()
        view.setModel(model)

        Shiboken.invalidate(parent)

        self.assertFalse(Shiboken.isValid(parent))
        self.assertFalse(Shiboken.isValid(view))
        self.assertTrue(Shiboken.isValid(model))

    def testInvalidateParentOfReferenceHolder(self):
        '''The walk must survive a decref cascade it sets off itself.'''
        # Detaching a child hands the parent reference back, and that decref
        # can be the last one. The child has to stay readable until the walk
        # is done with it, which is what the plan pins it for.
        parent = ObjectType.create()
        view = ObjectView.create()
        view.setParent(parent)
        view.setModel(ObjectModel.create())
        # The view is not kept on the Python side from here on: it lives on
        # its parent's reference, and that is the last one.
        del view
        self.assertTrue(Shiboken.isValid(parent))

        Shiboken.invalidate(parent)
        gc.collect()

        self.assertFalse(Shiboken.isValid(parent))


if __name__ == '__main__':
    unittest.main()
