# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QImage'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QImage
from helper.usesqapplication import UsesQApplication
from xpm_data import xpm


class QImageTest(UsesQApplication):
    '''Test case for calling setPixel with float as argument'''

    def testQImageStringBuffer(self):
        '''Test if the QImage signatures receiving string buffers exist.'''
        file = Path(__file__).resolve().parent / 'sample.png'
        self.assertTrue(file.is_file())
        img0 = QImage(file)

        # btw let's test the bits() method
        img1 = QImage(img0.bits(), img0.width(), img0.height(), img0.format())
        img1.setColorSpace(img0.colorSpace())
        self.assertEqual(img0, img1)
        img2 = QImage(img0.bits(), img0.width(), img0.height(), img0.bytesPerLine(), img0.format())
        img2.setColorSpace(img0.colorSpace())
        self.assertEqual(img0, img2)

        ## test scanLine method
        data1 = img0.scanLine(0)
        data2 = img1.scanLine(0)
        self.assertEqual(data1, data2)

    def testEmptyBuffer(self):
        img = QImage(bytes('', "UTF-8"), 100, 100, QImage.Format_ARGB32)

    def testEmptyStringAsBuffer(self):
        img = QImage(bytes('', "UTF-8"), 100, 100, QImage.Format_ARGB32)

    def testXpmConstructor(self):
        img = QImage(xpm)
        self.assertFalse(img.isNull())
        self.assertEqual(img.width(), 27)
        self.assertEqual(img.height(), 22)


if __name__ == '__main__':
    unittest.main()
