# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Property, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

is_pypy = hasattr(sys, "pypy_version_info")
if not is_pypy:
    from PySide6.support import feature

"""
snake_prop_feature_test.py
--------------------------

Test the snake_case and true_property feature.

This works now, including class properties.
"""


class Window(QWidget):
    def __init__(self):
        super().__init__()


@unittest.skipIf(is_pypy, "__feature__ cannot yet be used with PyPy")
class FeatureTest(unittest.TestCase):
    def setUp(self):
        qApp or QApplication()
        feature.reset()

    def tearDown(self):
        feature.reset()
        qApp.shutdown()

    def testRenamedFunctions(self):
        window = Window()
        window.setWindowTitle('camelCase')

        # and now the same with snake_case enabled
        from __feature__ import snake_case

        # Works with the same window! window = Window()
        window.set_window_title('snake_case')

    def testPropertyAppearVanish(self):
        window = Window()

        self.assertTrue(callable(window.isModal))
        with self.assertRaises(AttributeError):
            window.modal

        from __feature__ import snake_case, true_property
        #PYSIDE-1548: Make sure that another import does not clear the features.
        import sys

        self.assertTrue(isinstance(QWidget.modal, property))
        self.assertTrue(isinstance(window.modal, bool))
        with self.assertRaises(AttributeError):
            window.isModal

        # switching back
        feature.reset()

        self.assertTrue(callable(window.isModal))
        with self.assertRaises(AttributeError):
            window.modal

    def testClassProperty(self):
        from __feature__ import snake_case, true_property
        # We check the class...
        self.assertEqual(type(QApplication.quit_on_last_window_closed), bool)
        x = QApplication.quit_on_last_window_closed
        QApplication.quit_on_last_window_closed = not x
        self.assertEqual(QApplication.quit_on_last_window_closed, not x)
        # ... and now the instance.
        self.assertEqual(type(qApp.quit_on_last_window_closed), bool)
        x = qApp.quit_on_last_window_closed
        qApp.quit_on_last_window_closed = not x
        self.assertEqual(qApp.quit_on_last_window_closed, not x)
        # make sure values are equal
        self.assertEqual(qApp.quit_on_last_window_closed,
                         QApplication.quit_on_last_window_closed)

    def testUserClassNotAffected(self):
        FunctionType = type(lambda: 42)
        # Note: the types module does not have MethodDescriptorType in low versions.
        MethodDescriptorType = type(str.split)

        class UserClass(QWidget):

            def someFunc1(self):
                pass

            @staticmethod
            def someFunc2(a, b):
                pass

        inspect = UserClass.__dict__
        self.assertTrue(isinstance(inspect["someFunc1"], FunctionType))
        self.assertTrue(isinstance(inspect["someFunc2"], staticmethod))
        self.assertTrue(isinstance(UserClass.someFunc2, FunctionType))
        self.assertTrue(isinstance(UserClass.addAction, MethodDescriptorType))

        from __feature__ import snake_case

        inspect = UserClass.__dict__
        self.assertTrue(isinstance(inspect["someFunc1"], FunctionType))
        self.assertTrue(isinstance(inspect["someFunc2"], staticmethod))
        self.assertTrue(isinstance(UserClass.someFunc2, FunctionType))
        self.assertTrue(isinstance(UserClass.add_action, MethodDescriptorType))

    def testTrueProperyCanOverride(self):
        from __feature__ import true_property

        class CustomWidget(QWidget):
            global prop_result
            prop_result = None

            @Property(QSize)
            def minimumSizeHint(self):
                global prop_result
                print("called")
                prop_result = super().minimumSizeHint
                return prop_result

        window = QMainWindow()
        window.setCentralWidget(CustomWidget(window))
        window.show()
        self.assertTrue(isinstance(prop_result, QSize))


if __name__ == '__main__':
    unittest.main()
