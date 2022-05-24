# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6

# This test tests the new "macro" feature of qApp.
# It also uses the qApp variable to finish the instance and start over.

# Note: this test makes qapplication_singleton_test.py obsolete.


class qAppMacroTest(unittest.TestCase):
    _test_1093_is_first = True

    def test_qApp_is_like_a_macro_and_can_restart(self):
        self._test_1093_is_first = False
        from PySide6 import QtCore
        try:
            from PySide6 import QtGui, QtWidgets
        except ImportError:
            QtWidgets = QtGui = QtCore
        # qApp is in the builtins
        self.assertEqual(bool(qApp), False)
        # and the type is None
        self.assertTrue(qApp is None)
        # now we create an application for all cases
        classes = (QtCore.QCoreApplication,
                   QtGui.QGuiApplication,
                   QtWidgets.QApplication)
        fil = sys.stderr
        for klass in classes:
            print("CREATED", klass([]), file=fil)
            fil.flush()
            qApp.shutdown()
            print("DELETED qApp", qApp, file=fil)
            fil.flush()
        # creating without deletion raises:
        QtCore.QCoreApplication([])
        with self.assertRaises(RuntimeError):
            QtCore.QCoreApplication([])
        self.assertEqual(QtCore.QCoreApplication.instance(), qApp)

    def test_1093(self):
        # Test that without creating a QApplication staticMetaObject still exists.
        # Please see https://bugreports.qt.io/browse/PYSIDE-1093 for explanation.
        # Note: This test must run first, otherwise we would be mislead!
        assert self._test_1093_is_first
        from PySide6 import QtCore
        self.assertTrue(QtCore.QObject.staticMetaObject is not None)
        app = QtCore.QCoreApplication.instance()
        self.assertTrue(QtCore.QObject.staticMetaObject is not None)
        if app is None:
            app = QtCore.QCoreApplication([])
        self.assertTrue(QtCore.QObject.staticMetaObject is not None)
        qApp.shutdown()


if __name__ == '__main__':
    unittest.main()
