#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""Tests covering signal emission and receiving to python slots"""

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QSpinBox, QPushButton

from helper.basicpyslotcase import BasicPySlotCase
from helper.usesqapplication import UsesQApplication


class ButtonPySlot(UsesQApplication, BasicPySlotCase):
    """Tests the connection of python slots to QPushButton signals"""

    def testButtonClicked(self):
        """Connection of a python slot to QPushButton.clicked()"""
        button = QPushButton('Mylabel')
        button.clicked.connect(self.cb)
        self.args = tuple()
        button.clicked.emit()
        self.assertTrue(self.called)

    def testButtonClick(self):
        """Indirect qt signal emission using the QPushButton.click() method """
        button = QPushButton('label')
        button.clicked.connect(self.cb)
        self.args = tuple()
        button.click()
        self.assertTrue(self.called)


class SpinBoxPySlot(UsesQApplication, BasicPySlotCase):
    """Tests the connection of python slots to QSpinBox signals"""

    def setUp(self):
        super(SpinBoxPySlot, self).setUp()
        self.spin = QSpinBox()

    def tearDown(self):
        del self.spin
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(SpinBoxPySlot, self).tearDown()

    def testSpinBoxValueChanged(self):
        """Connection of a python slot to QSpinBox.valueChanged(int)"""
        self.spin.valueChanged.connect(self.cb)
        self.args = [3]
        self.spin.valueChanged.emit(*self.args)
        self.assertTrue(self.called)

    def testSpinBoxValueChangedImplicit(self):
        """Indirect qt signal emission using QSpinBox.setValue(int)"""
        self.spin.valueChanged.connect(self.cb)
        self.args = [42]
        self.spin.setValue(self.args[0])
        self.assertTrue(self.called)

    def atestSpinBoxValueChangedFewArgs(self):
        """Emission of signals with fewer arguments than needed"""
        self.spin.valueChanged.connect(self.cb)
        self.args = (554,)
        self.assertRaises(TypeError, self.spin.valueChanged.emit)


class QSpinBoxQtSlots(UsesQApplication):
    """Tests the connection to QSpinBox qt slots"""

    qapplication = True

    def testSetValueIndirect(self):
        """Indirect signal emission: QSpinBox using valueChanged(int)/setValue(int)"""
        spinSend = QSpinBox()
        spinRec = QSpinBox()

        spinRec.setValue(5)

        spinSend.valueChanged.connect(spinRec.setValue)
        self.assertEqual(spinRec.value(), 5)
        spinSend.setValue(3)
        self.assertEqual(spinRec.value(), 3)
        self.assertEqual(spinSend.value(), 3)

    def testSetValue(self):
        """Direct signal emission: QSpinBox using valueChanged(int)/setValue(int)"""
        spinSend = QSpinBox()
        spinRec = QSpinBox()

        spinRec.setValue(5)
        spinSend.setValue(42)

        spinSend.valueChanged.connect(spinRec.setValue)
        self.assertEqual(spinRec.value(), 5)
        self.assertEqual(spinSend.value(), 42)
        spinSend.valueChanged.emit(3)

        self.assertEqual(spinRec.value(), 3)
        # Direct emission shouldn't change the value of the emitter
        self.assertEqual(spinSend.value(), 42)

        spinSend.valueChanged.emit(66)
        self.assertEqual(spinRec.value(), 66)
        self.assertEqual(spinSend.value(), 42)


if __name__ == '__main__':
    unittest.main()
