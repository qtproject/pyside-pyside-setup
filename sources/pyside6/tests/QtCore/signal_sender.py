# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import (QCoreApplication, QObject, QStringListModel,
                            QTimer, Signal, Slot, Qt)


class Sender(QObject):
    testSignal = Signal()

    def emitSignal(self):
        self.testSignal.emit()


class Receiver(QObject):

    def __init__(self, parent=None):
        super().__init__()
        self._sender = None
        self._slot_count = 0

    @Slot()
    def testSlot(self):
        self._sender = self.sender()
        self._slot_count += 1


class DerivedReceiver(Receiver):
    pass


class TestSignalSender(UsesQApplication):
    """Test PYSIDE-2144/1295, check that QObject::sender() works also if it is
       routed via GlobalReceiverV2 in case of a non-C++ slot (Python callback,
       as for derived classes)."""
    def testSignalSender(self):
        sender = Sender()
        receiver = Receiver()
        sender.testSignal.connect(receiver.testSlot)
        derived_receiver = DerivedReceiver()
        sender.testSignal.connect(derived_receiver.testSlot)
        sender.emitSignal()

        QTimer.singleShot(100, self.app.quit)
        while derived_receiver._slot_count == 0:
            QCoreApplication.processEvents()

        self.assertEqual(receiver._sender, sender)
        self.assertEqual(derived_receiver._sender, sender)


class TestConstructorConnection(UsesQApplication):
    """PYSIDE-2329: Check constructor connections for signals from the
       base as well as signals with arguments."""
    def testConstructorConnection(self):

        was_destroyed = False
        was_changed = False

        def destroyed_handler():
            nonlocal was_destroyed
            was_destroyed = True

        def changed_handler():
            nonlocal was_changed
            was_changed = True

        data_list = ["blub"]
        model = QStringListModel(data_list,
                                 destroyed=destroyed_handler,
                                 dataChanged=changed_handler)
        model.setData(model.index(0, 0), "bla", Qt.EditRole)
        del model

        self.assertTrue(was_changed)
        self.assertTrue(was_destroyed)


if __name__ == '__main__':
    unittest.main()
