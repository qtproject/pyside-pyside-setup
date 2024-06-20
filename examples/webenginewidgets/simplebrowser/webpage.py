# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from functools import partial

from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineCertificateError
from PySide6.QtCore import QTimer, Signal


class WebPage(QWebEnginePage):

    create_certificate_error_dialog = Signal(QWebEngineCertificateError)

    def __init__(self, profile, parent):
        super().__init__(profile, parent)

        self.selectClientCertificate.connect(self.handle_select_client_certificate)
        self.certificateError.connect(self.handle_certificate_error)

    def _emit_create_certificate_error_dialog(self, error):
        self.create_certificate_error_dialog.emit(error)

    def handle_certificate_error(self, error):
        error.defer()
        QTimer.singleShot(0, partial(self._emit_create_certificate_error_dialog, error))

    def handle_select_client_certificate(self, selection):
        # Just select one.
        selection.select(selection.certificates()[0])
