# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QRandomGenerator, QRandomGenerator64


class QRandomGeneratorTest(unittest.TestCase):
    '''Test case for QRandomGenerator'''

    def testGenerator(self):
        self.assertTrue(QRandomGenerator.system())
        self.assertTrue(QRandomGenerator.global_())
        generator = QRandomGenerator()
        r = generator.bounded(10, 20)
        self.assertTrue(r >= 10)
        self.assertTrue(r <= 20)

    def testGenerator64(self):
        generator = QRandomGenerator64()
        r = generator.generate()


if __name__ == '__main__':
    unittest.main()
