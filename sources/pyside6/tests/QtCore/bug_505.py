# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class MyBaseObject(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.setObjectName("PySide")

    def __del__(self):
        if self.objectName() != "PySide":
            raise NameError('Fail')


class CheckForEventsTypes(unittest.TestCase):
    def testDelObject(self):
        p = MyBaseObject()
        o = MyBaseObject(p)
        del o
        del p
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()


if __name__ == '__main__':
    unittest.main()
