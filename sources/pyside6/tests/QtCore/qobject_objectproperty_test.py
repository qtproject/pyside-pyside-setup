#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for the bug #378
http://bugs.openbossa.org/show_bug.cgi?id=378
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class ExtQObject(QObject):
    def __init__(self):
        # "foobar" will become a object attribute that will not be
        # listed on the among the type attributes. Thus for bug
        # condition be correctly triggered the "foobar" attribute
        # must not previously exist in the parent class.
        self.foobar = None
        # The parent __init__ method must be called after the
        # definition of "self.foobar".
        super().__init__()


class TestBug378(unittest.TestCase):
    '''Test case for the bug #378'''

    def testBug378(self):
        obj = ExtQObject()


if __name__ == '__main__':
    unittest.main()

