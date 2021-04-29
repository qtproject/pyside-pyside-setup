#############################################################################
##
## Copyright (C) 2017 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqapplication import TimedQApplication
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QColor
from PySide6.QtQuick import QQuickItem, QQuickView


class TestGrabToSharedPointerImage(TimedQApplication):
    def setUp(self):
        TimedQApplication.setUp(self, 1000)

    def testQQuickItemGrabToImageSharedPointer(self):
        view = QQuickView()
        file = Path(__file__).resolve().parent / 'qquickitem_grabToImage.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(os.fspath(file)))
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
            QTimer.singleShot(0, self.app.quit)

            # Show the grabbed image in the QML Image item.
            imageContainer.setProperty("source", grabResultSharedPtr.url())

        # Wait for signal when grabbing is complete.
        grabResultSharedPtr.ready.connect(onGrabReady)
        self.app.exec_()

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
