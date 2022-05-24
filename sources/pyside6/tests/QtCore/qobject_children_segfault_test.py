# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for parent-child relationship'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QCoreApplication


class ChildrenCoreApplication(unittest.TestCase):
    '''Test case for calling QObject.children after creating a QCoreApp'''

    def testQCoreAppChildren(self):
        # QObject.children() after creating a QCoreApplication
        # Minimal test:
        # 1- Create QCoreApp
        # 2- Create parent and childrens
        # 3- While keeping the children alive, call parent.children()
        # 4- Delete parent
        app = QCoreApplication([])
        parent = QObject()
        children = [QObject(parent) for x in range(25)]
        # Uncomment the lines below to make the test pass
        # del children
        # del child2
        del parent  # XXX Segfaults here
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
