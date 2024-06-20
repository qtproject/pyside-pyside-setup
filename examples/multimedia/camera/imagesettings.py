# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtMultimedia import QImageCapture
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QSize

from ui_imagesettings import Ui_ImageSettingsUi


def box_value(box):
    idx = box.currentIndex()
    return None if idx == -1 else box.itemData(idx)


def select_combo_box_item(box, value):
    idx = box.findData(value)
    if idx != -1:
        box.setCurrentIndex(idx)


class ImageSettings(QDialog):

    def __init__(self, imageCapture, parent=None):
        super().__init__(parent)
        self.imagecapture = imageCapture
        self._ui = Ui_ImageSettingsUi()
        self._ui.setupUi(self)

        # image codecs
        self._ui.imageCodecBox.addItem("Default image format",
                                       QImageCapture.UnspecifiedFormat)
        supported_image_formats = QImageCapture.supportedFormats()
        for f in supported_image_formats:
            description = QImageCapture.fileFormatDescription(f)
            name = QImageCapture.fileFormatName(f)
            self._ui.imageCodecBox.addItem(f"{name} : {description}", f)

        self._ui.imageQualitySlider.setRange(0, QImageCapture.VeryHighQuality.value)

        self._ui.imageResolutionBox.addItem("Default Resolution", QSize())
        camera = imageCapture.captureSession().camera()
        supported_resolutions = camera.cameraDevice().photoResolutions()
        for resolution in supported_resolutions:
            w, h = resolution.width(), resolution.height()
            self._ui.imageResolutionBox.addItem(f"{w}x{h}", resolution)

        select_combo_box_item(self._ui.imageCodecBox, imageCapture.fileFormat())
        select_combo_box_item(self._ui.imageResolutionBox, imageCapture.resolution())
        self._ui.imageQualitySlider.setValue(imageCapture.quality().value)

    def apply_image_settings(self):
        self.imagecapture.setFileFormat(box_value(self._ui.imageCodecBox))
        q = self._ui.imageQualitySlider.value()
        self.imagecapture.setQuality(QImageCapture.Quality(q))
        self.imagecapture.setResolution(box_value(self._ui.imageResolutionBox))
