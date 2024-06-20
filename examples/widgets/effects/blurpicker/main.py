# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the widgets/effects/blurpicker example from Qt v6.x"""

import sys
from PySide6.QtWidgets import QApplication
from blurpicker import BlurPicker


if __name__ == "__main__":
    app = QApplication(sys.argv)

    blur_picker = BlurPicker()
    blur_picker.setWindowTitle("Application Picker")

    blur_picker.setFixedSize(400, 300)
    blur_picker.show()

    sys.exit(app.exec())
