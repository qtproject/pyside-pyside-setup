# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import QFile, QIODevice, QObject, QSize, Qt


class QPixmapTest(UsesQApplication):
    def testQVariantConstructor(self):
        obj = QObject()
        pixmap = QPixmap()
        obj.setProperty('foo', pixmap)
        self.assertEqual(type(obj.property('foo')), QPixmap)

    def testQSizeConstructor(self):
        pixmap = QPixmap(QSize(10, 20))
        self.assertTrue(pixmap.size().height(), 20)

    def testQStringConstructor(self):
        pixmap = QPixmap("Testing!")

    def testQPixmapLoadFromDataWithQFile(self):
        f = QFile(os.path.join(os.path.dirname(__file__), 'sample.png'))
        self.assertTrue(f.open(QIODevice.ReadOnly))
        data = f.read(f.size())
        f.close()
        pixmap = QPixmap()
        self.assertTrue(pixmap.loadFromData(data))

    def testQPixmapLoadFromDataWithPython(self):
        data = open(os.path.join(os.path.dirname(__file__), 'sample.png'), 'rb').read()
        pixmap = QPixmap()
        self.assertTrue(pixmap.loadFromData(data))


class QPixmapToImage(UsesQApplication):

    def testFilledImage(self):
        '''QPixmap.fill + toImage + image.pixel'''
        pixmap = QPixmap(100, 200)
        pixmap.fill(Qt.red)  # Default Qt.white

        self.assertEqual(pixmap.height(), 200)
        self.assertEqual(pixmap.width(), 100)

        image = pixmap.toImage()

        self.assertEqual(image.height(), 200)
        self.assertEqual(image.width(), 100)

        pixel = image.pixel(10, 10)
        self.assertEqual(pixel, QColor(Qt.red).rgba())


if __name__ == '__main__':
    unittest.main()

