# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' unit test for BUG #1313 '''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


class MyQObject(QObject):
    sig = Signal()


demo_coroutine_definition_code = """
async def demo_coroutine():
    my_qobject = MyQObject()
    my_qobject.sig.connect(lambda: None)
"""


exec(demo_coroutine_definition_code)


class CoroutineRaisesStopIterationTestCase(unittest.TestCase):
    def setUp(self):
        self.coroutine = demo_coroutine()

    def testCoroutine(self):
        with self.assertRaises(StopIteration):
            self.coroutine.send(None)


def demo_generator():
    my_qobject = MyQObject()
    my_qobject.sig.connect(lambda: None)
    return
    yield  # to make it a generator


class GeneratorRaisesStopIterationTestCase(unittest.TestCase):
    def setUp(self):
        self.generator = demo_generator()

    def testGenerator(self):
        with self.assertRaises(StopIteration):
            self.generator.send(None)


if __name__ == "__main__":
    unittest.main()
