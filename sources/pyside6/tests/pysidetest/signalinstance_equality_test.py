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

from PySide6.QtCore import QFile, QObject, QTimer, Signal, SignalInstance, Slot
from PySide6.QtWidgets import QSlider


class C(QObject):
    custom_signal = Signal()


class D(C):
    pass


class TestSignalInstance(unittest.TestCase):
    def test_signal_instances_are_equal(self):
        o = QTimer()
        self.assertTrue(o.timeout == o.timeout)

    def test_inherited_signal_instances_are_equal(self):
        o = QFile()
        self.assertTrue(o.readyRead == o.readyRead)

    def test_custom_signal_instances_are_equal(self):
        o = C()
        self.assertTrue(o.custom_signal == o.custom_signal)

    def test_custom_inherited_signal_instances_are_equal(self):
        o = D()
        self.assertTrue(o.custom_signal == o.custom_signal)
    # additional tests of old errors from 2010 or so
    def test_uninitialized_SignalInstance(self):
        # This will no longer crash
        print(SignalInstance())
        with self.assertRaises(RuntimeError):
            SignalInstance().connect(lambda: None)
        with self.assertRaises(RuntimeError):
            SignalInstance().disconnect()
        with self.assertRaises(RuntimeError):
            SignalInstance().emit()

class MyWidget(QSlider):
    valueChanged = Signal(tuple)

    def __init__(self):
        super().__init__()
        self.valueChanged.connect(self._on_change)

    def setValue(self, value):
        self.valueChanged.emit(value)

    @Slot()
    def _on_change(self, new_value):
        print("new_value:", new_value)
        global result
        result = new_value


class TestRightOrder(UsesQApplication):
    def test_rightOrder(self):
        wdg = MyWidget()

        # PYSIDE-1751: Fixes the wrong behavior we got on >=6.2
        #     PySide <=6.1.3 prints "new_value: (30, 40)"
        #     PySide >=6.2 prints "new_value: 0"
        wdg.setValue((30, 40))
        self.assertEqual(result, (30, 40))


if __name__ == '__main__':
    unittest.main()
