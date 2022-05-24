# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Property, Slot

'''Tests that the signal notify id of a property is correct, aka corresponds to the initially set
notify method.'''


class Foo(QObject):
    def __init__(self):
        super().__init__()
        self._prop = "Empty"

    def getProp(self):
        return self._prop

    def setProp(self, value):
        if value != self._prop:
            self._prop = value
            self.propChanged.emit()

    # Inside the dynamic QMetaObject, the methods have to be sorted, so that this slot comes
    # after any signals. That means the property notify id has to be updated, to have the correct
    # relative method id.
    @Slot()
    def randomSlot():
        pass

    propChanged = Signal()
    prop = Property(str, getProp, setProp, notify=propChanged)


class NotifyIdSignal(unittest.TestCase):
    def setUp(self):
        self.obj = Foo()

    def tearDown(self):
        del self.obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testSignalEmission(self):
        metaObject = self.obj.metaObject()
        propertyIndex = metaObject.indexOfProperty("prop")
        property = metaObject.property(propertyIndex)

        signalIndex = property.notifySignalIndex()
        signal = metaObject.method(signalIndex)
        signalName = signal.name()
        self.assertEqual(signalName, "propChanged")


if __name__ == '__main__':
    unittest.main()
