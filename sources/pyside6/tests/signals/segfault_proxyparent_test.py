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

from PySide6.QtCore import QObject, SIGNAL

# Description of the problem
# After creating an PyObject that inherits from QObject, connecting it,
# deleting it and later creating another Python QObject-based object, this
# new object will point to the same memory position as the first one.

# Somehow the underlying QObject also points to the same position.

# In PyQt4, the connection works fine with the same memory behavior,
# so it looks like specific to SIP.


class Dummy(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)


class Joe(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)


class SegfaultCase(unittest.TestCase):
    """Test case for the segfault happening when parent() is called inside
    ProxyObject"""

    def setUp(self):
        self.called = False

    def tearDown(self):
        try:
            del self.args
        except:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testSegfault(self):
        """Regression: Segfault for qobjects in the same memory position."""
        obj = Dummy()
        QObject.connect(obj, SIGNAL('bar(int)'), self.callback)
        self.args = (33,)
        obj.emit(SIGNAL('bar(int)'), self.args[0])
        self.assertTrue(self.called)
        del obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        obj = Joe()
        QObject.connect(obj, SIGNAL('bar(int)'), self.callback)
        self.args = (33,)
        obj.emit(SIGNAL('bar(int)'), self.args[0])
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()

