#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
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

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL


class MyObject(QObject):
    pass


class TestSignalLimitless(unittest.TestCase):
    SIGNAL_MAX = 100

    def test100DynamicSignals(self):

        self.count = 0

        def onSignal():
            self.count += 1

        # create 100 dynamic signals
        o = MyObject()
        for i in range(self.SIGNAL_MAX):
            o.connect(SIGNAL(f'sig{i}()'), onSignal)

        # check if the signals are valid
        m = o.metaObject()
        for i in range(self.SIGNAL_MAX):
            self.assertTrue(m.indexOfSignal(f'sig{i}()') > 0)

        # emit all 100 signals
        for i in range(self.SIGNAL_MAX):
            o.emit(SIGNAL(f'sig{i}()'))

        self.assertEqual(self.count, self.SIGNAL_MAX)


if __name__ == '__main__':
    unittest.main()
