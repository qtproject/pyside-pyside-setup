#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from PySide6.QtCore import QMetaMethod, QObject, Signal  # noqa: E402


class Whatever(QObject):
    """Test class. The slot is not decorated so that it is dynamically added
       right before using setattr() to add a signal in the respective copy of
       the dynamic meta object."""

    echoSignal = Signal(str)

    def __init__(self):
        super().__init__()
        self.echoSignal.connect(self.mySlot)

    def mySlot(self, v):
        pass


class LateSignalTest(unittest.TestCase):
    ''' PYSIDE-315: Test that adding a signal after class creation is rejected.
        Signals are named and registered while the type is parsed. A Signal
        assigned to the class afterwards never reaches the meta object: it used
        to bind to an instance with the signature "()", which Qt connects by
        index without checking arguments, so emitting it read arguments that
        were never written. Binding such a signal must fail instead.'''

    def testLateSignalRejected(self):
        obj = Whatever()
        # Insert a signal after the type has been parsed.
        setattr(Whatever, "foo", Signal())
        with self.assertRaises(RuntimeError) as cm:
            obj.foo
        self.assertIn("added after the class was created", str(cm.exception))

    def testDeclaredSignalStillWorks(self):
        obj = Whatever()
        received = []
        obj.echoSignal.connect(received.append)
        obj.echoSignal.emit("hello")
        self.assertEqual(received, ["hello"])


class WarningTest(unittest.TestCase):
    '''PYSIDE-315: Test that signal/slots are in right order even when adding
       a signal after a slot, adapting to
       qtbase/a05c9bbb3f1fd15e74fbebe00ea0e3d5b4944967'''

    def testSignalSlotWarning(self):
        # we create an object. This gives no warning.
        obj = Whatever()
        # then we insert a signal after mySlot() has been created.
        setattr(Whatever, "foo", Signal(name="foo"))
        obj.foo.connect(obj.mySlot)

        # Verify that signals are in front
        metaObject = obj.metaObject()
        while metaObject:
            last_method_type = QMetaMethod.MethodType.Signal
            for m in range(metaObject.methodOffset(), metaObject.methodCount()):
                method_type = metaObject.method(m).methodType()
                self.assertFalse(method_type == QMetaMethod.MethodType.Signal
                                 and last_method_type == QMetaMethod.Slot)
                last_method_type = method_type
            metaObject = metaObject.superClass()


if __name__ == "__main__":
    unittest.main()
