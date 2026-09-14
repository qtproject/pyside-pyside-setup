# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject


class Filter(TestObject):

    def __init__(self):
        super().__init__(0)
        self.received = None
        self.received_type_name = ''

    def graphicsEventFilter(self, item):
        self.received_type_name = type(item).__name__


class MultiInheritanceTest(unittest.TestCase):
    """Create a QGraphicsProxyWidget in C++ (ensuring no wrapper map entry exists),
       send it through a virtual function taking a 'QGraphicsItem *' and test it is
       received as QGraphicsProxyWidget (considering the pointer offset from the
       multiple inheritance QObject/QGraphicsItem)."""
    def testMultiInheritance(self):
        filter = Filter()
        filter.sendGraphicsProxyWidgetThroughEventFilter()
        self.assertEqual(filter.received_type_name, "QGraphicsProxyWidget")


if __name__ == '__main__':
    unittest.main()
