# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QCoreApplication, QUrl

import rc_viewer  # noqa: F401

"""PySide6 port of the pdf/pdfviewer example from Qt v6.x"""


if __name__ == "__main__":
    name = "Qt Quick PDF Viewer Example"
    QCoreApplication.setApplicationName(name)
    QCoreApplication.setOrganizationName("QtProject")

    app = QGuiApplication(sys.argv)

    dir = Path(__file__).resolve().parent

    argument_parser = ArgumentParser(description=name,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("file", help="The file to open",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()

    url = None
    if options.file:
        url = QUrl.fromLocalFile(options.file)
    else:
        url = QUrl.fromLocalFile(os.fspath(dir / "resources" / "test.pdf"))

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"source": url})

    engine.load(QUrl.fromLocalFile(os.fspath(dir / "viewer.qml")))
    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = QCoreApplication.exec()
    del engine
    sys.exit(exit_code)
