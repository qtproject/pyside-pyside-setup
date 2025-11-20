# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 Multimedia player example"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qVersion, QCoreApplication, QDir, QUrl

from player import Player


if __name__ == "__main__":
    app = QApplication(sys.argv)

    QCoreApplication.setApplicationName("Player Example")
    QCoreApplication.setOrganizationName("QtProject")
    QCoreApplication.setApplicationVersion(qVersion())
    argument_parser = ArgumentParser(description=QCoreApplication.applicationName(),
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("file", help="File", nargs='?', type=str)
    options = argument_parser.parse_args()

    player = Player()
    if options.file:
        player.openUrl(QUrl.fromUserInput(options.file, QDir.currentPath(),
                       QUrl.UserInputResolutionOption.AssumeLocalFile))
    player.show()
    sys.exit(QCoreApplication.exec())
