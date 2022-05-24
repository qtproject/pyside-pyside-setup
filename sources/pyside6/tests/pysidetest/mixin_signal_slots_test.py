#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' PYSIDE-315: https://bugreports.qt.io/browse/PYSIDE-315
    Test that all signals and slots of a class (including any mixin classes)
    are registered at type parsing time. Also test that the signal and slot
    indices do not change after signal connection or emission. '''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Slot


class Mixin(object):
    mixinSignal = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MixinTwo(Mixin):
    mixinTwoSignal = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mixinTwoSlotCalled = False

    @Slot()
    def mixinTwoSlot(self):
        self.mixinTwoSlotCalled = True


class MixinThree(object):
    mixinThreeSignal = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mixinThreeSlotCalled = False

    @Slot()
    def mixinThreeSlot(self):
        self.mixinThreeSlotCalled = True


class Derived(Mixin, QObject):
    derivedSignal = Signal(str)

    def __init__(self):
        super().__init__()
        self.derivedSlotCalled = False
        self.derivedSlotString = ''

    @Slot(str)
    def derivedSlot(self, theString):
        self.derivedSlotCalled = True
        self.derivedSlotString = theString


class MultipleDerived(MixinTwo, MixinThree, Mixin, QObject):
    derivedSignal = Signal(str)

    def __init__(self):
        super().__init__()
        self.derivedSlotCalled = False
        self.derivedSlotString = ''

    @Slot(str)
    def derivedSlot(self, theString):
        self.derivedSlotCalled = True
        self.derivedSlotString = theString


class MixinTest(unittest.TestCase):
    def testMixinSignalSlotRegistration(self):
        obj = Derived()
        m = obj.metaObject()

        # Should contain 2 signals and 1 slot immediately after type parsing
        self.assertEqual(m.methodCount() - m.methodOffset(), 3)

        # Save method indices to check that they do not change
        methodIndices = {}
        for i in range(m.methodOffset(), m.methodCount()):
            signature = m.method(i).methodSignature()
            methodIndices[signature] = i

        # Check derivedSignal emission
        obj.derivedSignal.connect(obj.derivedSlot)
        obj.derivedSignal.emit('emit1')
        self.assertTrue(obj.derivedSlotCalled)
        obj.derivedSlotCalled = False

        # Check derivedSignal emission after mixingSignal connection
        self.outsideSlotCalled = False

        @Slot()
        def outsideSlot():
            self.outsideSlotCalled = True

        obj.mixinSignal.connect(outsideSlot)
        obj.derivedSignal.emit('emit2')
        self.assertTrue(obj.derivedSlotCalled)
        self.assertFalse(self.outsideSlotCalled)
        obj.derivedSlotCalled = False

        # Check mixinSignal emission
        obj.mixinSignal.emit()
        self.assertTrue(self.outsideSlotCalled)
        self.assertFalse(obj.derivedSlotCalled)
        self.outsideSlotCalled = False

        # Check that method indices haven't changed.
        # Make sure to requery for the meta object, to check that a new one was not
        # created as a child of the old one.
        m = obj.metaObject()
        self.assertEqual(m.methodCount() - m.methodOffset(), 3)
        for i in range(m.methodOffset(), m.methodCount()):
            signature = m.method(i).methodSignature()
            self.assertEqual(methodIndices[signature], i)

    def testMixinSignalSlotRegistrationWithMultipleInheritance(self):
        obj = MultipleDerived()
        m = obj.metaObject()

        # Should contain 4 signals and 3 slots immediately after type parsing
        self.assertEqual(m.methodCount() - m.methodOffset(), 7)

        # Save method indices to check that they do not change
        methodIndices = {}
        for i in range(m.methodOffset(), m.methodCount()):
            signature = m.method(i).methodSignature()
            methodIndices[signature] = i

        # Check derivedSignal emission
        obj.derivedSignal.connect(obj.derivedSlot)
        obj.derivedSignal.emit('emit1')
        self.assertTrue(obj.derivedSlotCalled)
        self.assertFalse(obj.mixinTwoSlotCalled)
        self.assertFalse(obj.mixinThreeSlotCalled)
        obj.derivedSlotCalled = False

        # Check derivedSignal emission after mixinThreeSignal connection
        self.outsideSlotCalled = False

        @Slot()
        def outsideSlot():
            self.outsideSlotCalled = True

        obj.mixinThreeSignal.connect(obj.mixinThreeSlot)
        obj.mixinThreeSignal.connect(outsideSlot)
        obj.derivedSignal.emit('emit2')
        self.assertTrue(obj.derivedSlotCalled)
        self.assertFalse(obj.mixinTwoSlotCalled)
        self.assertFalse(obj.mixinThreeSlotCalled)
        self.assertFalse(self.outsideSlotCalled)
        obj.derivedSlotCalled = False

        # Check mixinThreeSignal emission
        obj.mixinThreeSignal.emit()
        self.assertTrue(self.outsideSlotCalled)
        self.assertTrue(obj.mixinThreeSlotCalled)
        self.assertFalse(obj.derivedSlotCalled)
        self.assertFalse(obj.mixinTwoSlotCalled)
        self.outsideSlotCalled = False
        obj.mixinThreeSlotCalled = False

        # Check mixinTwoSignal emission
        obj.mixinTwoSignal.connect(obj.mixinTwoSlot)
        obj.mixinTwoSignal.emit()
        self.assertTrue(obj.mixinTwoSlotCalled)
        self.assertFalse(obj.mixinThreeSlotCalled)
        self.assertFalse(obj.derivedSlotCalled)
        self.assertFalse(self.outsideSlotCalled)
        obj.mixinTwoSlotCalled = False

        # Check mixinSignal emission
        obj.mixinSignal.connect(outsideSlot)
        obj.mixinSignal.emit()
        self.assertTrue(self.outsideSlotCalled)
        self.assertFalse(obj.mixinTwoSlotCalled)
        self.assertFalse(obj.mixinThreeSlotCalled)
        self.assertFalse(obj.derivedSlotCalled)
        self.outsideSlotCalled = False

        # Check that method indices haven't changed.
        # Make sure to requery for the meta object, to check that a new one was not
        # created as a child of the old one.
        m = obj.metaObject()
        self.assertEqual(m.methodCount() - m.methodOffset(), 7)
        for i in range(m.methodOffset(), m.methodCount()):
            signature = m.method(i).methodSignature()
            self.assertEqual(methodIndices[signature], i)


if __name__ == '__main__':
    unittest.main()

