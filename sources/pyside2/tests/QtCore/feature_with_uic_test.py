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

"""
feature_with_uic_test.py
------------------------

Check if feature switching works with a normal UIC file.
This crashed due to callbacks into QApplication.

PYSIDE-1626: Switch early in `BindingManager::getOverride`.
"""

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide2.QtCore import QCoreApplication, QLibraryInfo, qVersion
from PySide2.QtWidgets import QApplication, QMainWindow

if sys.version_info[0] >= 3:
    from __feature__ import snake_case

from feature_with_uic.window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class FeatureTest(UsesQApplication):

    def testFeaturesWorkWithUIC(self):
        window = MainWindow()
        window.set_window_title(qVersion())
        window.show()
        while not window.window_handle().is_exposed():
            QCoreApplication.process_events()


if __name__ == '__main__' and sys.version_info[0] >= 3:
    unittest.main()
