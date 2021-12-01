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

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QFont
from helper.usesqguiapplication import UsesQGuiApplication


class QFontTest(UsesQGuiApplication):

    def testStringConstruction(self):
        """PYSIDE-1685: Test that passing str to QFont works after addding
           QFont(QStringList) by qtbase/d8602ce58b6ef268be84b9aa0166b0c3fa6a96e8"""
        font_name = 'Times Roman'
        font = QFont(font_name)
        families = font.families()
        self.assertEqual(len(families), 1)
        self.assertEqual(families[0], font_name)

        font = QFont([font_name])
        families = font.families()
        self.assertEqual(len(families), 1)
        self.assertEqual(families[0], font_name)


if __name__ == '__main__':
    unittest.main()
