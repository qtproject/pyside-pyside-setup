# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Document Viewer demo from Qt v6.x"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication

from mainwindow import MainWindow


DESCRIPTION = "A viewer for JSON, PDF and text files"


if __name__ == "__main__":

    app = QApplication([])
    QCoreApplication.setOrganizationName("QtExamples")
    QCoreApplication.setApplicationName("DocumentViewer")
    QCoreApplication.setApplicationVersion("1.0")

    arg_parser = ArgumentParser(description=DESCRIPTION,
                                formatter_class=RawTextHelpFormatter)
    arg_parser.add_argument("file", type=str, nargs="?",
                            help="JSON, PDF or text file to open")
    args = arg_parser.parse_args()
    fileName = args.file

    w = MainWindow()
    w.show()
    if args.file and not w.openFile(args.file):
        sys.exit(-1)

    sys.exit(app.exec())
