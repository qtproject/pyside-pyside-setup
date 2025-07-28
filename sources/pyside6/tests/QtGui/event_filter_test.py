# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QWindow


class MyFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            pass
        return QObject.eventFilter(self, obj, event)


class EventFilter(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCount(self):
        o = QObject()
        base_ref_count = sys.getrefcount(o)
        filt = MyFilter()
        o.installEventFilter(filt)
        self.assertEqual(sys.getrefcount(o), base_ref_count)

        o.installEventFilter(filt)
        self.assertEqual(sys.getrefcount(o), base_ref_count)

        o.removeEventFilter(filt)
        self.assertEqual(sys.getrefcount(o), base_ref_count)

    def testObjectDestructorOrder(self):
        w = QWindow()
        filt = MyFilter()
        filt.app = self.app
        w.installEventFilter(filt)
        w.show()
        w.close()
        w = None
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
