#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests to test QTranslator and translation in general.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTranslator, QCoreApplication

from helper.usesqapplication import UsesQApplication


class TranslationTest(UsesQApplication):
    '''Test case for Qt translation facilities.'''

    def setUp(self):
        super(TranslationTest, self).setUp()
        self.trdir = os.path.join(os.path.dirname(__file__), 'translations')

    def testLatin(self):
        # Set string value to Latin
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_latin.qm'))
        self.app.installTranslator(translator)

        obj = QObject()
        obj.setObjectName(obj.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'Orbis, te saluto!')

    def testLatinClass(self):
        # Set string value to Latin, no instance
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_latin.qm'))
        self.app.installTranslator(translator)

        obj = QObject()
        obj.setObjectName(QObject.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'Orbis, te saluto!')

    def testLatinDerived(self):
        # PYSIDE-131: Test that derived classes work, too.
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_latin.qm'))
        self.app.installTranslator(translator)

        class Derived(QObject):
            pass

        obj = Derived()
        obj.setObjectName(obj.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'Orbis, te saluto!')

    def testLatinDerivedClass(self):
        # PYSIDE-131: Test that derived classes work, too, no instance.
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_latin.qm'))
        self.app.installTranslator(translator)

        class Derived(QObject):
            pass

        obj = Derived()
        obj.setObjectName(Derived.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'Orbis, te saluto!')

    def testRussian(self):
        # Set string value to Russian
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_russian.qm'))
        self.app.installTranslator(translator)

        obj = QObject()
        obj.setObjectName(obj.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'привет мир!')

    def testUtf8(self):
        translator = QTranslator()
        translator.load(os.path.join(self.trdir, 'trans_russian.qm'))
        self.app.installTranslator(translator)

        obj = QObject()
        obj.setObjectName(obj.tr('Hello World!'))
        self.assertEqual(obj.objectName(), 'привет мир!')

    def testTranslateWithNoneDisambiguation(self):
        value = 'String here'
        obj = QCoreApplication.translate('context', value, None)
        self.assertTrue(isinstance(obj, str))
        self.assertEqual(obj, value)


if __name__ == '__main__':
    unittest.main()

