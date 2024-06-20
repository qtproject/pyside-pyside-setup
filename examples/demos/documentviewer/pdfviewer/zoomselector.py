# Copyright (C) 2017 Klaralvdalens Datakonsult AB (KDAB).
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal, Slot
from PySide6.QtPdfWidgets import QPdfView


ZOOM_LEVELS = ["Fit Width", "Fit Page", "12%", "25%", "33%", "50%", "66%",
               "75%", "100%", "125%", "150%", "200%", "400%"]


class ZoomSelector(QComboBox):
    zoomModeChanged = Signal(QPdfView.ZoomMode)
    zoomFactorChanged = Signal(float)

    def __init__(self, parent):
        super().__init__(parent)
        self.setEditable(True)

        for z in ZOOM_LEVELS:
            self.addItem(z)

        self.currentTextChanged.connect(self.onCurrentTextChanged)
        self.lineEdit().editingFinished.connect(self._editingFinished)

    @Slot()
    def _editingFinished(self):
        self.onCurrentTextChanged(self.lineEdit().text())

    @Slot(float)
    def setZoomFactor(self, zoomFactor):
        z = int(100 * zoomFactor)
        self.setCurrentText(f"{z}%")

    @Slot()
    def reset(self):
        self.setCurrentIndex(8)  # 100%

    @Slot(str)
    def onCurrentTextChanged(self, text):
        if text == "Fit Width":
            self.zoomModeChanged.emit(QPdfView.ZoomMode.FitToWidth)
        elif text == "Fit Page":
            self.zoomModeChanged.emit(QPdfView.ZoomMode.FitInView)
        else:
            factor = 1.0
            withoutPercent = text.replace('%', '')
            zoomLevel = int(withoutPercent)
            if zoomLevel:
                factor = zoomLevel / 100.0

            self.zoomModeChanged.emit(QPdfView.ZoomMode.Custom)
            self.zoomFactorChanged.emit(factor)
