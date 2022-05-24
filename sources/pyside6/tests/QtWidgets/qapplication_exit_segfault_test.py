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

from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QSpinBox


class QApplicationDelete(unittest.TestCase):
    '''Test for segfault when deleting a QApplication before a QWidget'''

    def testQPushButton(self):
        # QApplication deleted before QPushButton
        a = QApplication([])
        b = QPushButton('aaaa')
        del a
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()


if __name__ == '__main__':
    unittest.main()
