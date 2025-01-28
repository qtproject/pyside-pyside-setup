# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QLineEdit, QSizePolicy, QWidget, QVBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import QUrl, Qt, Slot

from webpage import WebPage


class WebPopupWindow(QWidget):

    def __init__(self, view, profile, parent=None):
        super().__init__(parent, Qt.Window)
        self._url_line_edit = QLineEdit()
        self._fav_action = QAction(self)
        self._view = view

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._url_line_edit)
        layout.addWidget(self._view)

        self._view.setPage(WebPage(profile, self._view))
        self._view.setFocus()

        self._url_line_edit.setReadOnly(True)
        self._url_line_edit.addAction(self._fav_action, QLineEdit.ActionPosition.LeadingPosition)

        self._view.titleChanged.connect(self.setWindowTitle)
        self._view.urlChanged.connect(self._url_changed)
        self._view.fav_icon_changed.connect(self._fav_action.setIcon)
        p = self._view.page()
        p.geometryChangeRequested.connect(self.handle_geometry_change_requested)
        p.windowCloseRequested.connect(self.close)

    @Slot(QUrl)
    def _url_changed(self, url):
        self._url_line_edit.setText(url.toDisplayString())

    def view(self):
        return self._view

    def handle_geometry_change_requested(self, newGeometry):
        window = self.windowHandle()
        if window:
            self.setGeometry(newGeometry.marginsRemoved(window.frameMargins()))
        self.show()
        self._view.setFocus()
