#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for deleting a child object in python'''

import gc
import os
import random
import string
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType


class DeleteChildInPython(unittest.TestCase):
    '''Test case for deleting (unref) a child in python'''

    def testDeleteChild(self):
        '''Delete child in python should not invalidate child'''
        parent = ObjectType()
        child = ObjectType(parent)
        name = ''.join(random.sample(string.ascii_letters, 5))
        child.setObjectName(name)

        del child
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        new_child = parent.children()[0]
        self.assertEqual(new_child.objectName(), name)

if __name__ == '__main__':
    unittest.main()
