# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for QPixelFormat'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QImage, QPixelFormat, qPixelFormatRgba


class QPixelFormatTest(UsesQApplication):
    def test(self):
        image = QImage(QSize(200, 200), QImage.Format_ARGB32)
        image.fill(QColor(Qt.red))
        pixelFormat = image.pixelFormat()
        print(pixelFormat.greenSize())
        self.assertEqual(pixelFormat.alphaSize(), 8)
        self.assertEqual(pixelFormat.redSize(), 8)
        self.assertEqual(pixelFormat.greenSize(), 8)
        self.assertEqual(pixelFormat.blueSize(), 8)
        self.assertEqual(pixelFormat.bitsPerPixel(), 32)

    def testHelpers(self):
        format = qPixelFormatRgba(8, 8, 8, 8, QPixelFormat.UsesAlpha,
                                  QPixelFormat.AtBeginning, QPixelFormat.Premultiplied,
                                  QPixelFormat.UnsignedByte)
        self.assertEqual(format.redSize(), 8)


if __name__ == '__main__':
    unittest.main()
