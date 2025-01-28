# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt WebEngineWidgets Simple Browser example from Qt v6.x"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication, QLoggingCategory, QUrl

from browser import Browser

import data.rc_simplebrowser  # noqa: F401


if __name__ == "__main__":
    parser = ArgumentParser(description="Qt Widgets Web Browser",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--single-process", "-s", action="store_true",
                        help="Run in single process mode (trouble shooting)")
    parser.add_argument("url", type=str, nargs="?", help="URL")
    args = parser.parse_args()

    QCoreApplication.setOrganizationName("QtExamples")

    app_args = sys.argv
    if args.single_process:
        app_args.extend(["--webEngineArgs", "--single-process"])
    app = QApplication(app_args)
    app.setWindowIcon(QIcon(":AppLogoColor.png"))
    QLoggingCategory.setFilterRules("qt.webenginecontext.debug=true")

    s = QWebEngineProfile.defaultProfile().settings()
    s.setAttribute(QWebEngineSettings.PluginsEnabled, True)
    s.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
    s.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)

    browser = Browser()
    window = browser.create_hidden_window()

    url = QUrl.fromUserInput(args.url) if args.url else QUrl("chrome://qt")
    window.tab_widget().set_url(url)
    window.show()

    sys.exit(app.exec())
