# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the examples/serialbus/modbus/client example from Qt v6.x"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

from PySide6.QtCore import QCoreApplication, QLoggingCategory
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow


if __name__ == "__main__":
    parser = ArgumentParser(prog="Modbus Client Example",
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Generate more output")
    options = parser.parse_args()
    if options.verbose:
        QLoggingCategory.setFilterRules("qt.modbus* = true")

    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(QCoreApplication.exec())
