#!/usr/bin/python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import gc
import os
import sys
import sysconfig
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal

"""PYSIDE-2221: a receiver whose type supports no weak reference.

A bound method of such a receiver cannot be held through a weakref, so the
dynamic slot takes the other way: a strong reference on the whole callable.
That keeps the receiver alive for as long as the connection, where the raw
pointer this used to store merely outlived it.

Free-threaded builds only, and answering to FreeThreading::MethodReceiverUpgrade
like the rest of that work. A build with a GIL still binds the raw receiver
here; that the connection then outlives the receiver is that build's own
defect and is fixed in a change of its own.
"""


MSG_SKIP = "Only for GIL disabled builds."


def is_gil_disabled():
    gil_disabled_build = sysconfig.get_config_vars('Py_GIL_DISABLED')[0]
    return gil_disabled_build and not sys._is_gil_enabled()


class Sender(QObject):
    fired = Signal(int)


class SlottedReceiver:
    """__slots__ without __weakref__: PyWeakref_NewRef raises TypeError on
    an instance of this, which is the branch under test."""

    __slots__ = ("hits", )

    def __init__(self):
        self.hits = 0

    def handler(self, value):
        self.hits += value


@unittest.skipUnless(is_gil_disabled(), MSG_SKIP)
class WeakreflessReceiverTest(unittest.TestCase):

    def testTypeReallyHasNoWeakref(self):
        # If this ever stops holding, the test below stops testing anything.
        import weakref
        with self.assertRaises(TypeError):
            weakref.ref(SlottedReceiver())

    def testDeliveryAndOwnership(self):
        sender = Sender()
        receiver = SlottedReceiver()
        sender.fired.connect(receiver.handler)

        sender.fired.emit(1)
        self.assertEqual(receiver.hits, 1)

        # The connection owns the receiver, so dropping the last name for it
        # neither kills it nor leaves the slot with a dangling pointer.
        alive = receiver
        del receiver
        gc.collect()
        sender.fired.emit(2)
        self.assertEqual(alive.hits, 3)

    def testReceiverOwningItsSenderIsNotCollected(self):
        """The fallback's cost: a receiver owning its sender is not collected.

        The cycle runs through PySideQSlotObject, which the collector cannot
        walk. When the cycle becomes collectable, turn this around.
        See "Method slots own their receiver for the call" in the free-threading notes.
        """
        alive = []

        class Owner:
            __slots__ = ("sender", "hits")

            def __init__(self):
                self.hits = 0
                self.sender = Sender()
                self.sender.fired.connect(self.on_fired)

            def __del__(self):
                alive.clear()

            def on_fired(self, value):
                self.hits += value

        class WeakOwner(Owner):
            """The control: the same shape without __slots__, on the weakref path."""

        def run(cls, flag):
            obj = cls()
            flag.append(True)
            obj.sender.fired.emit(1)
            self.assertEqual(obj.hits, 1)
            del obj
            gc.collect()
            gc.collect()
            return bool(flag)

        control = []
        WeakOwner.__del__ = lambda self: control.clear()
        self.assertFalse(run(WeakOwner, control),
                         "the control did not get collected either - then "
                         "this test says nothing about the fallback")
        self.assertTrue(run(Owner, alive),
                        "the cycle became collectable - turn this test "
                        "around and drop the note in dynamicslot.cpp")

    def testDisconnectStops(self):
        sender = Sender()
        receiver = SlottedReceiver()
        sender.fired.connect(receiver.handler)
        sender.fired.disconnect(receiver.handler)
        sender.fired.emit(1)
        self.assertEqual(receiver.hits, 0)


if __name__ == '__main__':
    unittest.main()
