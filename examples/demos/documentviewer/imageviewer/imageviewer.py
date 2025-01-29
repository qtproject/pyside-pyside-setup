# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import math

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QDir, QSizeF
from PySide6.QtGui import (QPixmap, QImageReader, QIcon, QKeySequence,
                           QGuiApplication, QColorSpace, QPainter, QAction)

from abstractviewer import AbstractViewer


def imageFormats():
    result = []
    all_formats = QImageReader.supportedImageFormats()

    for format_bytes in all_formats:
        format_str = bytes(format_bytes).decode("utf-8")  # Convert QByteArray to str
        if format_str not in ["tif", "cur"]:  # Exclude duplicate/non-existent formats
            result.append(f"image/{format_str}")

    return result


def msgOpen(name, image):
    description = image.colorSpace().description() if image.colorSpace().isValid() else "unknown"
    return 'Opened "{0}", {1}x{2}, Depth: {3} ({4})'.format(
        QDir.toNativeSeparators(name),
        image.width(),
        image.height(),
        image.depth(),
        description
    )


class ImageViewer(AbstractViewer):

    def __init__(self):
        super().__init__()

        self.formats = imageFormats()
        self.uiInitialized.connect(self.setupImageUi)
        QImageReader.setAllocationLimit(1024)  # MB

    def init(self, file, parent, mainWindow):
        self.image_label = QLabel(parent)
        self.image_label.setFrameShape(QLabel.Box)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)

        # AbstractViewer.init(file, self.image_label, mainWindow)
        super().init(file, self.image_label, mainWindow)

        self.tool_bar = self.addToolBar(self.tr("Images"))

        icon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn,
                               QIcon(":/demos/documentviewer/images/zoom-in.png"))
        self.zoom_in_act = QAction(icon, "Zoom &In", self)
        self.zoom_in_act.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_act.triggered.connect(self.zoomIn)
        self.tool_bar.addAction(self.zoom_in_act)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut,
                               QIcon(":/demos/documentviewer/images/zoom-out.png"))
        self.zoom_out_act = QAction(icon, "Zoom &Out", self)
        self.zoom_out_act.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_act.triggered.connect(self.zoomOut)
        self.tool_bar.addAction(self.zoom_out_act)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomFitBest,
                               QIcon(":/demos/documentviewer/images/zoom-fit-best.png"))
        self.reset_zoom_act = QAction(icon, "Reset Zoom", self)
        self.reset_zoom_act.setShortcut(QKeySequence
                                        (Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_0))
        self.reset_zoom_act.triggered.connect(self.resetZoom)
        self.tool_bar.addAction(self.reset_zoom_act)

    def supportedMimeTypes(self):
        return self.formats

    def clear(self):
        self.image_label.setPixmap(QPixmap())
        self.max_scale_factor = self.min_scale_factor = 1
        self.initial_scale_factor = self.scale_factor = 1

    def setupImageUi(self):
        self.openFile()

    def openFile(self):

        QGuiApplication.setOverrideCursor(Qt.WaitCursor)

        name = self._file.fileName()
        reader = QImageReader(name)
        orig_image = reader.read()

        if orig_image.isNull():
            self.statusMessage(f"Cannot read file {name}:\n{reader.errorString()}", "open")
            self.disablePrinting()
            QGuiApplication.restoreOverrideCursor()
            return

        self.clear()

        if orig_image.colorSpace().isValid():
            image = orig_image.convertedToColorSpace(QColorSpace.SRgb)
        else:
            image = orig_image

        device_pixel_ratio = self.image_label.devicePixelRatioF()
        self.image_size = QSizeF(image.size()) / device_pixel_ratio

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        self.image_label.setPixmap(pixmap)

        target_size = self.image_label.parentWidget().size()
        if (self.image_size.width() > target_size.width()
                or self.image_size.height() > target_size.height()):
            self.initial_scale_factor = min(target_size.width() / self.image_size.width(),
                                            target_size.height() / self.image_size.height())

        self.max_scale_factor = 3 * self.initial_scale_factor
        self.min_scale_factor = self.initial_scale_factor / 3
        self.doSetScaleFactor(self.initial_scale_factor)

        self.statusMessage(msgOpen(name, orig_image))
        QGuiApplication.restoreOverrideCursor()

        self.maybeEnablePrinting()

    def setScaleFactor(self, scaleFactor):
        if not math.isclose(self.scale_factor, scaleFactor):
            self.doSetScaleFactor(scaleFactor)

    def doSetScaleFactor(self, scaleFactor):
        self.scale_factor = scaleFactor
        label_size = (self.image_size * self.scale_factor).toSize()
        self.image_label.setFixedSize(label_size)
        self.enableZoomActions()

    def zoomIn(self):
        self.setScaleFactor(self.scale_factor * 1.25)

    def zoomOut(self):
        self.setScaleFactor(self.scale_factor * 0.8)

    def resetZoom(self):
        self.setScaleFactor(self.initial_scale_factor)

    def hasContent(self):
        return not self.image_label.pixmap().isNull()

    def enableZoomActions(self):
        self.reset_zoom_act.setEnabled(not math.isclose(self.scale_factor,
                                                        self.initial_scale_factor))
        self.zoom_in_act.setEnabled(self.scale_factor < self.max_scale_factor)
        self.zoom_out_act.setEnabled(self.scale_factor > self.min_scale_factor)

    def printDocument(self, printer):
        if not self.hasContent():
            return

        painter = QPainter(printer)
        pixmap = self.image_label.pixmap()
        rect = painter.viewport()
        size = pixmap.size()
        size.scale(rect.size(), Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
