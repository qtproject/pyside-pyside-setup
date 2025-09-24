# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlDebuggingEnabler
from PySide6.QtQuick import QQuickView

from TextBalloon.textballoon import TextBalloon  # noqa: F401

if __name__ == "__main__":
    argument_parser = ArgumentParser(description="Scene Graph Painted Item Example",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("-qmljsdebugger", action="store",
                                 help="Enable QML debugging")
    options = argument_parser.parse_args()
    if options.qmljsdebugger:
        QQmlDebuggingEnabler.enableDebugging(True)

    app = QGuiApplication(sys.argv)
    QCoreApplication.setOrganizationName("QtProject")
    QCoreApplication.setOrganizationDomain("qt-project.org")

    view = QQuickView()
    view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    view.engine().addImportPath(Path(__file__).parent)
    view.loadFromModule("painteditemexample", "Main")

    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)
    view.show()

    exit_code = QCoreApplication.exec()
    del view
    sys.exit(exit_code)
