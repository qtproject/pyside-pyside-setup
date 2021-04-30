#!/usr/bin/env python

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

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QMainWindow
from helper.timedqapplication import TimedQApplication


class Signaller(QObject):
    s1 = Signal()
    s2 = Signal()
    s3 = Signal()


class Window(object):

    def __init__(self, s):
        self._window = QMainWindow()
        self._window.setAttribute(Qt.WA_DeleteOnClose, True)
        self._window.setWindowTitle("Demo!")

        self._s = s
        self._s.s1.connect(self._on_signal)
        self._s.s2.connect(self._on_signal)

    def show(self):
        self._window.show()

    def _on_signal(self):
        self._window.setWindowTitle("Signaled!")


class TestTimedApp(TimedQApplication):
    def testSignals(self):
        s = Signaller()
        w = Window(s)
        w.show()

        def midleFunction():
            def internalFunction():
                pass
            s.s3.connect(internalFunction)

        midleFunction()
        self.app.exec()
        del w

        s.s1.emit()
        s.s2.emit()
        s.s3.emit()


if __name__ == '__main__':
    unittest.main()
