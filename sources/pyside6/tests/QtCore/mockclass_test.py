# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Test case for PySide bug 634
# http://bugs.pyside.org/show_bug.cgi?id=634
# Marcus Lindblom <macke@yar.nu>; 2011-02-16

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication


class Mock(object):
    def __init__(self):
        self.called = False
        self.return_value = None

    def __call__(self, *args, **kwargs):
        self.called = True
        return self.return_value


class MockClassTest(unittest.TestCase):
    def testMockQCoreApplication(self):
        mock = Mock()
        setattr(QCoreApplication, 'instance', mock)
        QCoreApplication.instance()
        self.assertTrue(mock.called)


if __name__ == '__main__':
    unittest.main()

