# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLayout

from spreadsheet import SpreadSheet

if __name__ == "__main__":
    app = QApplication()

    sheet = SpreadSheet(10, 6)
    sheet.setWindowIcon(QPixmap(":/images/interview.png"))
    sheet.show()
    sheet.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    sys.exit(app.exec())
