# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QDesktopServices'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


class QDesktopServicesTest(unittest.TestCase):
    def testOpenUrl(self):
        # At the bare minimum check that they return false for invalid url's
        url = QUrl()
        self.assertEqual(QDesktopServices.openUrl(url), False)


if __name__ == '__main__':
    unittest.main()
