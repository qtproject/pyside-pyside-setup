#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import ObjectType
from sample import ObjectView
from sample import ObjectModel



class ObjTest(unittest.TestCase):

    def test_cyclic_dependency_withParent(self):
        """Create 2 objects with a cyclic dependency, so that they can
        only be removed by the garbage collector, and then invoke the
        garbage collector in a different thread.
        """
        class CyclicChildObject(ObjectType):
            def __init__(self, parent):
                super(CyclicChildObject, self).__init__(parent)
                self._parent = parent

        class CyclicObject(ObjectType):
            def __init__(self):
                super(CyclicObject, self).__init__()
                CyclicChildObject(self)

        # turn off automatic garbage collection, to be able to trigger it
        # at the 'right' time
        gc.disable()
        alive = lambda :sum(isinstance(o, CyclicObject) for o in gc.get_objects() )

        #
        # first proof that the wizard is only destructed by the garbage
        # collector
        #
        cycle = CyclicObject()
        self.assertTrue(alive())
        del cycle
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: the semantics of gc.enable/gc.disable is different for PyPy
            self.assertTrue(alive())
        gc.collect()
        self.assertFalse(alive())

    def test_cyclic_dependency_withKeepRef(self):
        """Create 2 objects with a cyclic dependency, so that they can
        only be removed by the garbage collector, and then invoke the
        garbage collector in a different thread.
        """
        class CyclicChildObject(ObjectView):
            def __init__(self, model):
                super(CyclicChildObject, self).__init__(None)
                self.setModel(model)

        class CyclicObject(ObjectModel):
            def __init__(self):
                super(CyclicObject, self).__init__()
                self._view = CyclicChildObject(self)

        # turn off automatic garbage collection, to be able to trigger it
        # at the 'right' time
        gc.disable()
        alive = lambda :sum(isinstance(o, CyclicObject) for o in gc.get_objects() )

        #
        # first proof that the wizard is only destructed by the garbage
        # collector
        #
        cycle = CyclicObject()
        self.assertTrue(alive())
        del cycle
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: the semantics of gc.enable/gc.disable is different for PyPy
            self.assertTrue(alive())
        gc.collect()
        self.assertFalse(alive())

if __name__ == '__main__':
    unittest.main()

