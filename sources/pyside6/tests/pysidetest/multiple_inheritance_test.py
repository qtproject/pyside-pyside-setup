# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QMainWindow, QLabel


def xprint(*args, **kw):
    if "-v" in sys.argv:
        print(*args, **kw)

# This is the original testcase of PYSIDE-1564
class Age(object):
    def __init__(self, age=0, **kwds):
        super().__init__(**kwds)

        self.age = age

class Person(QtCore.QObject, Age):
    def __init__(self, name, **kwds):
        super().__init__(**kwds)

        self.name = name


class OriginalMultipleInheritanceTest(unittest.TestCase):

    def testIt(self):
        xprint()
        p = Person("Joe", age=38)
        xprint(f"p.age = {p.age}")
        # This would crash if MI does not work.

# More tests follow:

# mro ('C', 'A', 'QObject', 'Object', 'B', 'object')
class A(QtCore.QObject):
    def __init__(self, anna=77, **kw):
        xprint(f'A: before init kw = {kw}')
        super().__init__(**kw)
        xprint('A: after init')

class B:
    def __init__(self, otto=6, age=7, **kw):
        xprint(f'B: before init kw = {kw}')
        if "killme" in kw:
            raise AssertionError("asdf")
        super().__init__(**kw)
        self.age = age
        xprint('B: after init')

class C(A, B):
    def __init__(self, **kw):
        xprint(f'C: before init kw = {kw}')
        super().__init__(**kw)
        xprint('C: after init')

# mro ('F', 'D', 'QCursor', 'E', 'QLabel', 'QFrame', 'QWidget', 'QObject', 'QPaintDevice', 'Object', 'object')
class D(QtGui.QCursor):
    def __init__(self, anna=77, **kw):
        xprint(f'D: before init kw = {kw}')
        super().__init__(**kw)
        xprint('D: after init')

class E:
    def __init__(self, age=7, **kw):
        xprint(f'E: before init kw = {kw}')
        super().__init__(**kw)
        self.age = age
        xprint('E: after init')

class F(D, E, QtWidgets.QLabel):
    def __init__(self, **kw):
        xprint(f'F: before init kw = {kw}')
        super().__init__(**kw)
        xprint('F: after init')

# mro ('I', 'G', 'QTextDocument', 'H', 'QLabel', 'QFrame', 'QWidget', 'QObject', 'QPaintDevice', 'Object', 'object')
# Similar, but this time we want to reach `H` without support from `super`.
class G(QtGui.QTextDocument):
    pass

class H:
    def __init__(self, age=7, **kw):
        xprint(f'H: before init kw = {kw}')
        super().__init__(**kw)
        self.age = age
        xprint('H: after init')

class I(G, H, QtWidgets.QLabel):
    pass


# PYSIDE-2294: Friedemann's test adapted.
#              We need to ignore positional args in mixin classes.
class Ui_X_MainWindow(object):  # Emulating uic
    def setupUi(self, MainWindow):
        MainWindow.resize(400, 300)
        self.lbl = QLabel(self)

class MainWindow(QMainWindow, Ui_X_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class AdditionalMultipleInheritanceTest(UsesQApplication):

    def testABC(self):
        xprint()
        res = C(otto=3, anna=5)
        self.assertEqual(res.age, 7)
        xprint()
        with self.assertRaises(AssertionError):
            res=C(killme=42)
        xprint()

    def testDEF(self):
        xprint()
        res = F(anna=5)
        self.assertEqual(res.age, 7)
        xprint()

    def testGHI(self):
        xprint()
        res = I(age=7)
        self.assertEqual(res.age, 7)
        xprint()

    def testParentDoesNotCrash(self):
        # This crashed with
        # TypeError: object.__init__() takes exactly one argument (the instance to initialize)
        MainWindow()


if __name__ == "__main__":
    unittest.main()
