#############################################################################
##
## Copyright (C) 2017 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import inspect
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6.QtCore
import PySide6.QtWidgets
from PySide6.support.signature import get_signature


class PySideSignatureTest(unittest.TestCase):
    def testSignatureExist(self):
        t1 = type(get_signature(PySide6.QtCore.QObject.children))
        self.assertEqual(t1, inspect.Signature)
        t2 = type(get_signature(PySide6.QtCore.QObject.__dict__["children"]))
        self.assertEqual(t2, t1)
        obj = PySide6.QtWidgets.QApplication.palette
        t3 = type(get_signature(obj))
        self.assertEqual(t3, list)
        self.assertEqual(len(get_signature(obj)), 3)
        for thing in get_signature(obj):
            self.assertEqual(type(thing), inspect.Signature)
        sm = PySide6.QtWidgets.QApplication.__dict__["palette"]
        # PYSIDE-1436: staticmethod is a callable since Python 3.10
        # Instead of checking callable(sm), we check the type:
        self.assertEqual(type(sm), staticmethod)
        self.assertTrue(get_signature(sm) is not None)

    def testSignatureIsCached(self):
        # see if we get the same object
        ob1 = get_signature(PySide6.QtCore.QObject.children)
        ob2 = get_signature(PySide6.QtCore.QObject.children)
        self.assertTrue(ob1 is ob2)
        # same with multi signature
        ob1 = get_signature(PySide6.QtWidgets.QApplication.palette)
        ob2 = get_signature(PySide6.QtWidgets.QApplication.palette)
        self.assertTrue(ob1 is ob2)

    def testModuleIsInitialized(self):
        self.assertTrue(get_signature(PySide6.QtWidgets.QApplication) is not None)

    def test_NotCalled_is_callable_and_correct(self):
        # A signature that has a default value with some "Default(...)"
        # wrapper is callable and creates an object of the right type.
        sig = get_signature(PySide6.QtCore.QByteArray().toPercentEncoding)
        called_default = sig.parameters["exclude"].default()
        self.assertEqual(type(called_default), PySide6.QtCore.QByteArray)


if __name__ == "__main__":
    unittest.main()
