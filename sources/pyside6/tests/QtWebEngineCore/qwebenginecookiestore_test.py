# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

from helper.usesqapplication import UsesQApplication


class TestQWebEngineCookieStore(UsesQApplication):
    def testBasicFilter(self):
        self._loaded = False
        self._ok = False
        src_dir = Path(__file__).resolve().parent
        html_path = src_dir / "resources" / "index.html"
        view = QWebEngineView()
        cookie_store = view.page().profile().cookieStore()
        firstPartyUrlPaths = []

        def cookie_filter(request):
            nonlocal firstPartyUrlPaths
            firstPartyUrlPaths.append(Path(request.firstPartyUrl.toLocalFile()))
            return False

        cookie_store.setCookieFilter(cookie_filter)
        view.loadFinished.connect(self._slot_loaded)
        view.load(QUrl.fromLocalFile(html_path))
        view.show()
        QTimer.singleShot(10000, self.app.quit)
        self.app.exec()

        self.assertTrue(self._loaded, "Time out")
        self.assertTrue(self._ok, "Load error")
        self.assertEqual(len(firstPartyUrlPaths), 2)
        self.assertListEqual(firstPartyUrlPaths, [html_path, html_path])

    def _slot_loaded(self, ok):
        self._loaded = True
        self._ok = ok
        QApplication.quit()


if __name__ == '__main__':
    unittest.main()
