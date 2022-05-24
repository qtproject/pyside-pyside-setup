# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QLCDNumber


class QLCDNumberOverflow(unittest.TestCase):
    '''Test case for unhandled overflow on QLCDNumber() numDigits argument (see bug #215).'''

    def assertRaises(self, *args, **kwds):
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: PyPy complains "Fatal RPython error: NotImplementedError"
            return super().assertRaises(*args, **kwds)

    def setUp(self):
        self.app = QApplication([])

    def testnumDigitsOverflow(self):
        # NOTE: PyQt4 raises TypeError, but boost.python raises OverflowError
        self.assertRaises(OverflowError, QLCDNumber, 840835495615213080)


if __name__ == '__main__':
    unittest.main()
