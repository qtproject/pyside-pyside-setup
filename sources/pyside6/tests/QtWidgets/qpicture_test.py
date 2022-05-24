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
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPicture, QPainter
from PySide6.QtWidgets import QWidget


class MyWidget(QWidget):
    def paintEvent(self, e):
        with QPainter(self) as p:
            p.drawPicture(0, 0, self._picture)
        self._app.quit()


class QPictureTest(UsesQApplication):
    def testFromData(self):
        picture = QPicture()
        with QPainter(picture) as painter:
            painter.drawEllipse(10, 20, 80, 70)

        data = picture.data()
        picture2 = QPicture()
        picture2.setData(data)

        self.assertEqual(picture2.data(), picture.data())

        w = MyWidget()
        w._picture = picture2
        w._app = self.app

        QTimer.singleShot(300, w.show)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()

