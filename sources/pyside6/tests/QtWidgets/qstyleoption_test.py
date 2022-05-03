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

import sys
import os
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtWidgets import (QApplication, QCommonStyle, QPushButton)


text = ''


class Style(QCommonStyle):

    def drawControl(self, element, option, painter, widget=None):
        # This should be a QStyleOptionButton with a "text" field
        global text
        text = option.text


class StyleOptionTest(UsesQApplication):
    '''PYSIDE-1909: Test cast to derived style option classes.'''

    def testStyle(self):
        global text
        button = QPushButton("Hello World")
        button.setStyle(Style())
        button.show()
        while not text:
            QApplication.processEvents()
        self.assertEqual(text, button.text())


if __name__ == '__main__':
    unittest.main()
