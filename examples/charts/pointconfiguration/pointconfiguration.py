# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Light Markers Points Selection example from Qt v6.2"""
import sys
from PySide6.QtWidgets import QApplication

from chartwindow import ChartWindow


if __name__ == "__main__":

    a = QApplication(sys.argv)
    main_window = ChartWindow()
    main_window.resize(640, 480)
    main_window.show()
    sys.exit(a.exec())
