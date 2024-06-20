# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the widgets/richtext/textedit example from Qt v6.x"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtCore import QCoreApplication, qVersion
from PySide6.QtWidgets import QApplication

from textedit import TextEdit

import textedit_rc  # noqa: F401


if __name__ == '__main__':
    argument_parser = ArgumentParser(description='Rich Text Example',
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("file", help="File",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()

    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("QtProject")
    QCoreApplication.setApplicationName("Rich Text")
    QCoreApplication.setApplicationVersion(qVersion())

    mw = TextEdit()

    available_geometry = mw.screen().availableGeometry()
    mw.resize((available_geometry.width() * 2) / 3,
              (available_geometry.height() * 2) / 3)
    mw.move((available_geometry.width() - mw.width()) / 2,
            (available_geometry.height() - mw.height()) / 2)

    file = options.file if options.file else ":/example.html"
    if not mw.load(file):
        mw.file_new()

    mw.show()
    sys.exit(app.exec())
