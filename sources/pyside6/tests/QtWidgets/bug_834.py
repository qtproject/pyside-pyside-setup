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

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow


class Window(QMainWindow):
    def childEvent(self, event):
        super(Window, self).childEvent(event)


app = QApplication([])
window = Window()

dock1 = QDockWidget()
dock2 = QDockWidget()
window.addDockWidget(Qt.LeftDockWidgetArea, dock1)
window.addDockWidget(Qt.LeftDockWidgetArea, dock2)
window.tabifyDockWidget(dock1, dock2)

window.show()
QTimer.singleShot(0, window.close)
app.exec_()
