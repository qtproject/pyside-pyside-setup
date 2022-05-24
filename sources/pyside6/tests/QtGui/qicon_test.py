# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqguiapplication import TimedQGuiApplication
from PySide6.QtGui import QIcon


class QIconCtorWithNoneTest(TimedQGuiApplication):
    '''Test made by seblin, see Bug #944: http://bugs.pyside.org/show_bug.cgi?id=944'''

    def testQIconCtorWithNone(self):
        icon = QIcon(None)
        pixmap = icon.pixmap(48, 48)
        self.app.exec()


PIX_PATH = os.fspath(Path(__file__).resolve().parents[2]
                     / "doc/tutorials/basictutorial/icons.png")

class QIconAddPixmapTest(TimedQGuiApplication):
    '''PYSIDE-1669: check that addPixmap works'''

    def testQIconSetPixmap(self):
        icon = QIcon()
        icon.addPixmap(PIX_PATH)
        sizes = icon.availableSizes()
        self.assertTrue(sizes)

    def testQIconSetPixmapPathlike(self):
        icon = QIcon()
        pix_path = Path(PIX_PATH)
        icon.addPixmap(pix_path)
        sizes = icon.availableSizes()
        self.assertTrue(sizes)


if __name__ == '__main__':
    unittest.main()
