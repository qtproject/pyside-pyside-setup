#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
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

'''Test cases for passing invalid callbacks to QObject.connect'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL


class InvalidCallback(unittest.TestCase):
    '''Test case for passing an invalid callback to QObject.connect'''

    def setUp(self):
        # Acquire resources
        self.obj = QObject()

    def tearDown(self):
        # Release resources
        try:
            del self.obj
        except AttributeError:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testIntegerCb(self):
        # Test passing an int as callback to QObject.connect
        self.assertRaises(TypeError, QObject.connect, self.obj,
                            SIGNAL('destroyed()'), 42)


if __name__ == '__main__':
    unittest.main()

