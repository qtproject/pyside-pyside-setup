#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test case for a class that holds a unknown handle object.
    Test case for BUG #1105.
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import HandleHolder

class HandleHolderTest(unittest.TestCase):
    def testCreation(self):
        holder = HandleHolder(HandleHolder.createHandle())
        holder2 = HandleHolder(HandleHolder.createHandle())
        self.assertEqual(holder.compare(holder2), False)

    def testTransfer(self):
        holder = HandleHolder()
        holder2 = HandleHolder(holder.handle())
        self.assertTrue(holder.compare(holder2))

    def testUseDefinedType(self):
        holder = HandleHolder(8)
        holder2 = HandleHolder(holder.handle2())
        self.assertTrue(holder.compare2(holder2))

if __name__ == '__main__':
    unittest.main()
