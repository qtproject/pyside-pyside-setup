#!/usr/bin/python

#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

""" PYSIDE-1755: https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1755
    Tests that a unittest.mock.MagicMock() can be used as a slot for quick
    prototyping. """

import os
import sys
import unittest
from unittest.mock import MagicMock

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class MockAsSlot(unittest.TestCase):
    def testMockAsSlot(self):
        obj = QObject()
        mock = MagicMock()
        obj.objectNameChanged.connect(mock)

        obj.objectNameChanged.emit("test")
        mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
