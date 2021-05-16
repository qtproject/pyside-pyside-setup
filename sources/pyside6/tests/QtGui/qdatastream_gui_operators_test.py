# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QDataStream, QByteArray, QIODevice, Qt
from PySide6.QtGui import QPixmap, QColor

from helper.usesqapplication import UsesQApplication


class QPixmapQDatastream(UsesQApplication):
    '''QDataStream <<>> QPixmap'''

    def setUp(self):
        super(QPixmapQDatastream, self).setUp()
        self.source_pixmap = QPixmap(100, 100)
        # PYSIDE-1533: Use Qt.transparent to force Format_ARGB32_Premultiplied
        # when converting to QImage in any case.
        self.source_pixmap.fill(Qt.transparent)
        self.output_pixmap = QPixmap()
        self.buffer = QByteArray()
        self.read_stream = QDataStream(self.buffer, QIODevice.ReadOnly)
        self.write_stream = QDataStream(self.buffer, QIODevice.WriteOnly)

    def testStream(self):
        self.write_stream << self.source_pixmap

        self.read_stream >> self.output_pixmap

        image = self.output_pixmap.toImage()
        pixel = image.pixel(10, 10)
        self.assertEqual(pixel, QColor(Qt.transparent).rgba())
        self.assertEqual(self.source_pixmap.toImage(), image)


if __name__ == '__main__':
    unittest.main()
