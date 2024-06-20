# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QtMultiMedia camera example from Qt v6.x"""

import sys

from PySide6.QtWidgets import QApplication

from camera import Camera


if __name__ == "__main__":
    app = QApplication(sys.argv)
    camera = Camera()
    camera.show()
    sys.exit(app.exec())
