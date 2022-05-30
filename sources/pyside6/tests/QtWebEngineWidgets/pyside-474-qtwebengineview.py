# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from functools import partial
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(TEST_DIR))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QSize, QUrl, Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView


class MainTest(unittest.TestCase):

    def test_WebEngineView_findText_exists(self):
        app = QApplication.instance() or QApplication()
        top_level = QWidget()
        layout = QVBoxLayout(top_level)
        self._view = QWebEngineView()
        self._view.loadFinished.connect(self.loaded)
        self._view.load(QUrl.fromLocalFile(os.path.join(TEST_DIR, "fox.html")))
        self._view.setMinimumSize(QSize(400, 300))
        self._callback_count = 0
        layout.addWidget(self._view)
        top_level.show()
        app.exec()

    def found_callback(self, found):
        self.assertTrue(found)
        self._callback_count += 1
        if self._callback_count == 2:
            QCoreApplication.quit()

    def javascript_callback(self, result):
        self.assertEqual(result, "Title")
        self._callback_count += 1
        if self._callback_count == 2:
            QCoreApplication.quit()

    def loaded(self, ok):
        self.assertTrue(ok)
        if not ok:
            QCoreApplication.quit()
        self._view.page().runJavaScript("document.title", 1,
                                        partial(self.javascript_callback))
        self._view.findText("fox", QWebEnginePage.FindFlag(0),
                            partial(self.found_callback))


if __name__ == '__main__':
    unittest.main()
