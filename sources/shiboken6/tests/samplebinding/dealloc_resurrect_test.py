#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Tests looking a wrapper up from the map while it is being deallocated.'''

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType
from shiboken6 import Shiboken


class DeallocResurrectTest(unittest.TestCase):
    '''Tests looking a wrapper up from the map while it is being deallocated.

    A wrapper's refcount reaches zero and tp_dealloc starts, but the entry in
    the wrapper map is only removed several steps later, in deallocData(). In
    between, PyObject_ClearWeakRefs() runs Python code. Anything that looks the
    C++ pointer up in that window gets the dying wrapper handed back and
    increments its refcount - resurrecting it, while the deallocation carries
    on and frees it underneath. The second deallocation then works on freed
    memory.

    Single-threaded, no free-threading build required.
    '''

    def testLookupDuringDealloc(self):
        obj = ObjectType.create()
        ptr = Shiboken.getCppPointer(obj)[0]
        original = id(obj)
        seen = {}

        def callback(_ref):
            # Runs inside the wrapper's tp_dealloc, from ClearWeakRefs().
            seen['id'] = id(Shiboken.wrapInstance(ptr, ObjectType))

        ref = weakref.ref(obj, callback)
        del obj
        gc.collect()

        # The weakref has to be dead by now. Without this the test would also
        # pass when the callback never ran at all.
        self.assertIsNone(ref())
        # The lookup must not hand out the wrapper that is being destroyed.
        self.assertNotEqual(seen.get('id'), original)


if __name__ == '__main__':
    unittest.main()
