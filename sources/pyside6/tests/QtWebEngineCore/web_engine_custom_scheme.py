# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from PySide6.QtCore import QBuffer, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout  # noqa: E402
from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: E402
from PySide6.QtWebEngineCore import (QWebEngineProfile, QWebEngineUrlScheme,  # noqa: E402
                                     QWebEngineUrlSchemeHandler)  # noqa: E402


class TestSchemeHandler(QWebEngineUrlSchemeHandler):
    def requestStarted(self, request):
        if request.requestUrl() == "testpy:hello":
            request.redirect("testpy:goodbye")
            return

        self.buffer = QBuffer()
        self.buffer.setData(bytes("Really nice goodbye text.", "UTF-8"))
        self.buffer.aboutToClose.connect(self.buffer.deleteLater)
        request.reply(bytes("text/plain;charset=utf-8", "UTF-8"), self.buffer)


class MainTest(unittest.TestCase):
    def test_SchemeHandlerRedirect(self):
        self._loaded = False
        self._ok = False
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        app = QApplication([])

        scheme_name = bytes("testpy", "UTF-8")
        scheme = QWebEngineUrlScheme(scheme_name)
        scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
        QWebEngineUrlScheme.registerScheme(scheme)
        handler = TestSchemeHandler()
        profile = QWebEngineProfile.defaultProfile()
        profile.installUrlSchemeHandler(scheme_name, handler)

        top_level_widget = QWidget()
        top_level_widget.setWindowTitle('web_engine_custom_scheme.py')
        top_level_widget.resize(400, 400)
        layout = QVBoxLayout(top_level_widget)
        view = QWebEngineView()
        layout.addWidget(view)

        view.loadFinished.connect(self._slot_loaded)
        QTimer.singleShot(10000, app.quit)

        top_level_widget.show()
        view.load("testpy:hello")
        app.exec()

        self.assertTrue(self._loaded, "Time out")
        self.assertTrue(self._ok, "Load error")
        self.assertEqual(view.url(), "testpy:goodbye")

    def _slot_loaded(self, ok):
        self._loaded = True
        self._ok = ok
        QApplication.quit()


if __name__ == '__main__':
    unittest.main()
