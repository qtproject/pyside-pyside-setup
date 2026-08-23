#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Tests invalidating a parent whose child holds the last reference to another object.'''

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
    '''The invalidation walk collects the objects it has to visit, then runs the
    collected work with no lock held. Detaching a child hands the parent
    reference back, and that decref can be the last one: the child dies, its
    referred objects die with it, and anything the walk still had to visit
    through them is gone. This is a plain single-threaded crash, not a race.
    '''

    def testInvalidateParentOfReferenceHolder(self):
        '''The referred object must survive until the walk is done with it.'''
        # Both have to come from C++: an object constructed in Python carries a
        # C++ wrapper, and the invalidation walk skips those - it would never
        # reach the case under test.
        parent = ObjectType.create()
        view = ObjectView.create()
        view.setParent(parent)
        view.setModel(ObjectModel())
        # Neither the view nor the model is kept on the Python side from here
        # on: the view lives on its parent's reference, the model on the view's
        # reference map. Both are the last ones.
        del view
        self.assertTrue(Shiboken.isValid(parent))

        # Walks parent -> view -> model, detaches the view (dropping the last
        # reference to it, hence to the model), and then still has to visit
        # the model. Reaching the assertion at all is the point of the test.
        Shiboken.invalidate(parent)
        gc.collect()

        self.assertFalse(Shiboken.isValid(parent))


if __name__ == '__main__':
    unittest.main()
