# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""
PySide6 port of Qt6 example qtbase/examples/widgets/tools/regularexpression

More Information: https://doc.qt.io/qt-6/qtwidgets-tools-regularexpression-example.html
"""
import sys

from regularexpressiondialog import RegularExpressionDialog

from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = RegularExpressionDialog()
    dialog.show()

    sys.exit(app.exec())
