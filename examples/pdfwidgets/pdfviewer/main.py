# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QUrl

from mainwindow import MainWindow

"""PySide6 port of the pdfwidgets/pdfviewer example from Qt v6.x"""


if __name__ == "__main__":
    argument_parser = ArgumentParser(description="PDF Viewer",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("file", help="The file to open",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()

    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    if options.file:
        w.open(QUrl.fromLocalFile(options.file))
    sys.exit(QCoreApplication.exec())
