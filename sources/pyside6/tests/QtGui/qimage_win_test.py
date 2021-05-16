# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QImage/Windows'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from helper.usesqapplication import UsesQApplication


def create_image():
    result = QImage(20, 20, QImage.Format_RGB32)
    result.fill(Qt.white)
    return result


class QImageWinTest(UsesQApplication):

    def test_to_hbitmap(self):
        """Test conversion to/from a Windows HBITMAP."""

        image = create_image()
        hbitmap = image.toHBITMAP()
        self.assertTrue(hbitmap > 0)

        image2 = QImage.fromHBITMAP(hbitmap)
        image2.setColorSpace(image.colorSpace())
        self.assertEqual(image, image2)


if __name__ == '__main__':
    unittest.main()
