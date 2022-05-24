# Copyright (C) 2022 The Qt Company Ltd.
# Copyright (C) 2019 Andreas Beckermann
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import PySideCPP, TestObject


class QObjectDerivedReprTest(unittest.TestCase):
    """Test the __repr__ implementation of QObject derived classes"""

    def testReprWithoutNamespace(self):
        """Test that classes outside a namespace that have a operator<<(QDebug,...) defined use that
        for __repr__"""
        t = TestObject(123)

        # We don't define __str__, so str(q) should call __repr__
        self.assertEqual(t.__repr__(), str(t))

        # __repr__ should use the operator<<(QDebug,...) implementation
        self.assertIn('TestObject(id=123)', str(t))

    def testReprWithNamespace(self):
        """Test that classes inside a namespace that have a operator<<(QDebug,...) defined use that
        for __repr__"""
        t = PySideCPP.TestObjectWithNamespace(None)

        # We don't define __str__, so str(q) should call __repr__
        self.assertEqual(t.__repr__(), str(t))

        # __repr__ should use the operator<<(QDebug,...) implementation
        self.assertIn('TestObjectWithNamespace("TestObjectWithNamespace")', str(t))

    def testReprInject(self):
        """Test that injecting __repr__ via typesystem overrides the operator<<(QDebug, ...)"""
        t = PySideCPP.TestObject2WithNamespace(None)

        # We don't define __str__, so str(q) should call __repr__
        self.assertEqual(t.__repr__(), str(t))

        # __repr__ should use the operator<<(QDebug,...) implementation
        self.assertEqual(str(t), "TestObject2WithNamespace(injected_repr)")


if __name__ == '__main__':
    unittest.main()

