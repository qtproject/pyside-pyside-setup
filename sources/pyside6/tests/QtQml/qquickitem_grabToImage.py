# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QColor
from PySide6.QtQuick import QQuickItem, QQuickView


class TestGrabToSharedPointerImage(TimedQGuiApplication):
    def setUp(self):
        super().setUp(1000)

    def testQQuickItemGrabToImageSharedPointer(self):
        view = QQuickView()
        file = Path(__file__).resolve().parent / 'qquickitem_grabToImage.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()

        # Get the QQuickItem objects for the blue Rectangle and the Image item.
        root = view.rootObject()
        blueRectangle = root.findChild(QQuickItem, "blueRectangle")
        imageContainer = root.findChild(QQuickItem, "imageContainer")

        # Start the image grabbing.
        grabResultSharedPtr = blueRectangle.grabToImage()

        # Implicit call of operator bool() of the smart pointer, to check that it holds
        # a valid pointer.
        self.assertTrue(grabResultSharedPtr)

        self.grabbedColor = None

        def onGrabReady():
            # Signal early exit.
            QTimer.singleShot(50, self.app.quit)

            # Show the grabbed image in the QML Image item.
            imageContainer.setProperty("source", grabResultSharedPtr.url())

        # Wait for signal when grabbing is complete.
        grabResultSharedPtr.ready.connect(onGrabReady)
        self.app.exec()

        # Get the first pixel color of the grabbed image.
        self.image = grabResultSharedPtr.image()
        self.assertTrue(self.image)
        self.grabbedColor = self.image.pixelColor(0, 0)
        self.assertTrue(self.grabbedColor.isValid())

        # Compare the grabbed color with the one we set in the rectangle.
        blueColor = QColor("blue")
        self.assertEqual(self.grabbedColor, blueColor)


if __name__ == '__main__':
    unittest.main()
