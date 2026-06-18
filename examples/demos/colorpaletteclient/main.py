# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt RESTful API client demo from Qt v6.x"""

import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from basiclogin import BasicLogin  # noqa: F401
from paginatedresource import PaginatedResource  # noqa: F401
from restservice import RestService  # noqa: F401
import rc_colorpaletteclient  # noqa: F401

if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--url", type=str, help="The URL to open")
    args = parser.parse_args()
    url = args.url if args.url else "http://127.0.0.1:49425/api"

    app = QGuiApplication(sys.argv)
    QIcon.setThemeName("colorpaletteclient")

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"serverUrl": QUrl.fromUserInput(url)})

    app_dir = Path(__file__).parent
    app_dir_url = QUrl.fromLocalFile(os.fspath(app_dir))
    engine.addImportPath(os.fspath(app_dir))
    engine.loadFromModule("ColorPalette", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
