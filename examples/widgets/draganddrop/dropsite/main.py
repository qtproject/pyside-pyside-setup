# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from dropsitewindow import DropSiteWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DropSiteWindow()
    window.show()
    sys.exit(app.exec())
