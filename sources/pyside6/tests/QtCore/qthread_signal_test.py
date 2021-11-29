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

'''Test cases for connecting signals between threads'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QThread, QTimer, QObject, Signal, Slot, QCoreApplication


class Source(QObject):
    source = Signal()

    def __init__(self, *args):
        super().__init__(*args)

    @Slot()
    def emit_sig(self):
        self.source.emit()


class Target(QObject):
    def __init__(self, *args):
        super().__init__(*args)
        self.called = False

    @Slot()
    def myslot(self):
        self.called = True


class ThreadJustConnects(QThread):
    def __init__(self, source, *args):
        super().__init__(*args)
        self.source = source
        self.target = Target()

    def run(self):
        self.source.source.connect(self.target.myslot)
        self.source.source.connect(self.quit)
        self.exec()


class BasicConnection(unittest.TestCase):

    def testEmitOutsideThread(self):
        global thread_run

        app = QCoreApplication([])
        source = Source()
        thread = ThreadJustConnects(source)

        thread.finished.connect(QCoreApplication.quit)
        thread.start()

        QTimer.singleShot(50, source.emit_sig)
        app.exec()
        thread.wait()

        self.assertTrue(thread.target.called)


if __name__ == '__main__':
    unittest.main()
