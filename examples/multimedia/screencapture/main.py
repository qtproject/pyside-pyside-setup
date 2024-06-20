# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QtMultiMedia Screen Capture Example from Qt v6.x"""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from screencapturepreview import ScreenCapturePreview


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setApplicationName("screencapture")
    QCoreApplication.setOrganizationName("QtProject")
    screen_capture_preview = ScreenCapturePreview()
    screen_capture_preview.show()
    sys.exit(app.exec())
