# -*- coding: utf-8 -*-

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

'''Test cases for QResource usage'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QFile, QIODevice
import resources_mc

class ResourcesUsage(unittest.TestCase):
    '''Test case for resources usage'''

    def testPhrase(self):
        #Test loading of quote.txt resource
        file = Path(__file__).resolve().parent / 'quoteEnUS.txt'
        self.assertTrue(file.is_file())
        orig = QByteArray(file.read_bytes())
        # In case the file is checked out in 'crlf' mode, strip '\r'
        # since we read binary.
        if sys.platform == 'win32':
            carriage_return = orig.indexOf('\r')
            if carriage_return != -1:
                orig.remove(carriage_return, 1)

        f = QFile(':/quote.txt')  #|QIODevice.Text
        self.assertTrue(f.open(QIODevice.ReadOnly), f.errorString())
        copy = f.readAll()
        f.close()
        self.assertEqual(orig, copy)

    def testImage(self):
        #Test loading of sample.png resource
        file = Path(__file__).resolve().parent / 'sample.png'
        self.assertTrue(file.is_file())
        orig = file.read_bytes()

        f = QFile(':/sample.png')
        self.assertTrue(f.open(QIODevice.ReadOnly), f.errorString())
        copy = f.readAll()
        f.close()
        self.assertEqual(len(orig), len(copy))
        self.assertEqual(orig, copy)


if __name__ == '__main__':
    unittest.main()

