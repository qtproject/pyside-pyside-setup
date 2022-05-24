# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

from helper.usesqapplication import UsesQApplication


class TestQWebEngineCookieStore(UsesQApplication):
    def testBasicFilter(self):
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
        self.app.exec()

        self.assertEqual(len(firstPartyUrlPaths), 2)
        self.assertListEqual(firstPartyUrlPaths, [html_path, html_path])

    def _slot_loaded(self):
        QApplication.quit()


if __name__ == '__main__':
    unittest.main()
