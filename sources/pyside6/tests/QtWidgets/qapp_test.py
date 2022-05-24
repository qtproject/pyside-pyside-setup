# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test the presence of qApp Macro'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication


class QAppPresence(unittest.TestCase):

    def testQApp(self):
        # QtGui.qApp variable is instance of QApplication
        self.assertTrue(isinstance(qApp, QApplication))


def main():
    app = QApplication([])
    unittest.main()


if __name__ == '__main__':
    main()
