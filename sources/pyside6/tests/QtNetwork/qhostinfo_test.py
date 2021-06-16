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

'''Test case for QHostInfo.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqcoreapplication import UsesQCoreApplication
from PySide6.QtCore import (QCoreApplication, QElapsedTimer, QObject, QThread,
                            Slot, SLOT)
from PySide6.QtNetwork import QHostInfo


HOST = 'www.qt.io'


TIMEOUT = 30000


class Receiver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._slot_called = False

    def slot_called(self):
        return self._slot_called

    @Slot(QHostInfo)
    def info_received(self, host_info):
        name = host_info.hostName()
        if host_info.error() == QHostInfo.NoError:
            addresses = [a.toString() for a in host_info.addresses()]
            addresses_str = ', '.join(addresses)
            print(f'"{name}" resolved to {addresses_str}')
        else:
            error = host_info.errorString()
            print(f'Unable to resolve "{name}": {error}', file=sys.stderr)
        self._slot_called = True


class QHostInfoTest(UsesQCoreApplication):
    '''Test case for QHostInfo.'''
    def setUp(self):
        UsesQCoreApplication.setUp(self)
        self._timer = QElapsedTimer()

    def testStringBasedLookup(self):
        receiver = Receiver()
        self._timer.restart()
        QHostInfo.lookupHost(HOST, receiver, SLOT('info_received(QHostInfo)'))
        while not receiver.slot_called() and self._timer.elapsed() < TIMEOUT:
            QCoreApplication.processEvents()
            QThread.msleep(10)
        print(f'String-based: Elapsed {self._timer.elapsed()}ms')
        self.assertTrue(receiver.slot_called())

    def testCallableLookup(self):
        receiver = Receiver()
        self._timer.restart()
        QHostInfo.lookupHost(HOST, receiver.info_received)
        while not receiver.slot_called() and self._timer.elapsed() < TIMEOUT:
            QCoreApplication.processEvents()
            QThread.msleep(10)
        print(f'Callable: Elapsed {self._timer.elapsed()}ms')
        self.assertTrue(receiver.slot_called())


if __name__ == '__main__':
    unittest.main()
