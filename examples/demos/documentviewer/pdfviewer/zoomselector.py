# Copyright (C) 2017 Klaralvdalens Datakonsult AB (KDAB).
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import QLocale, Signal, Slot
from PySide6.QtPdfWidgets import QPdfView


ZOOM_LEVELS = [12, 25, 33, 50, 66, 75, 100, 125, 150, 200, 400]


class ZoomSelector(QComboBox):
    zoomModeChanged = Signal(QPdfView.ZoomMode)
    zoomFactorChanged = Signal(float)

    def __init__(self, parent):
        super().__init__(parent)

        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.setEditable(True)

        # ZoomMode::FitToWidth, ZoomMode::FitInView + factors
        for i in range(2 + len(ZOOM_LEVELS)):
            self.addItem("")

        self.retranslate()

        self.currentTextChanged.connect(self.onCurrentTextChanged)
        self.lineEdit().editingFinished.connect(self._editingFinished)

    def retranslate(self):
        i = 0
        self.setItemText(i, self.tr("Fit Width"))
        i += 1
        self.setItemText(i, self.tr("Fit Page"))
        i += 1
        percent = QLocale().percent()
        for z in ZOOM_LEVELS:
            self.setItemText(i, f"{z}{percent}")
            i += 1

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
        if text == self.itemText(0):
            self.zoomModeChanged.emit(QPdfView.ZoomMode.FitToWidth)
        elif text == self.itemText(1):
            self.zoomModeChanged.emit(QPdfView.ZoomMode.FitInView)
        else:
            factor = 1.0
            withoutPercent = text.replace(QLocale().percent(), '')
            zoomLevel = int(withoutPercent)
            if zoomLevel:
                factor = zoomLevel / 100.0

            self.zoomModeChanged.emit(QPdfView.ZoomMode.Custom)
            self.zoomFactorChanged.emit(factor)
