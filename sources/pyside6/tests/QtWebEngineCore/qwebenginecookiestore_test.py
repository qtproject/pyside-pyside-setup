#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################
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
