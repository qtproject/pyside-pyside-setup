# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtMultimedia import QMediaMetaData
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFileDialog,
                               QFormLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QScrollArea, QVBoxLayout, QWidget)
from PySide6.QtCore import QDateTime, QDir, Slot


IMAGE_FILTER = "Image Files (*.png *.jpg *.bmp)"


def default_value(key):
    if key == QMediaMetaData.Title:
        return "Qt Camera Example"
    if key == QMediaMetaData.Author:
        return "The Qt Company"
    if key == QMediaMetaData.Date:
        return QDateTime.currentDateTime().toString()
    return ""


class MetaDataDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_metaDataFields = []
        meta_data_layout = QFormLayout()
        for i in range(0, QMediaMetaData.NumMetaData):
            key = QMediaMetaData.Key(i)
            label = QMediaMetaData.metaDataKeyToString(QMediaMetaData.Key(key))
            line_edit = QLineEdit(default_value(key))
            line_edit.setClearButtonEnabled(True)
            self.m_metaDataFields.append(line_edit)
            if key == QMediaMetaData.ThumbnailImage:
                open_thumbnail = QPushButton("Open")
                open_thumbnail.clicked.connect(self.open_thumbnail_image)
                layout = QHBoxLayout()
                layout.addWidget(line_edit)
                layout.addWidget(open_thumbnail)
                meta_data_layout.addRow(label, layout)
            elif key == QMediaMetaData.CoverArtImage:
                open_cover_art = QPushButton("Open")
                open_cover_art.clicked.connect(self.open_cover_art_image)
                layout = QHBoxLayout()
                layout.addWidget(line_edit)
                layout.addWidget(open_cover_art)
                meta_data_layout.addRow(label, layout)
            else:
                meta_data_layout.addRow(label, line_edit)

        viewport = QWidget()
        viewport.setLayout(meta_data_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidget(viewport)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialog_layout.addWidget(button_box)

        self.setWindowTitle("Set Metadata")
        self.resize(400, 300)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    @Slot()
    def open_thumbnail_image(self):
        dir = QDir.currentPath()
        file_name = QFileDialog.getOpenFileName(self, "Open Image", dir,
                                                IMAGE_FILTER)
        if file_name:
            i = QMediaMetaData.ThumbnailImage.value
            self.m_metaDataFields[i].setText(file_name[0])

    @Slot()
    def open_cover_art_image(self):
        dir = QDir.currentPath()
        file_name = QFileDialog.getOpenFileName(self, "Open Image", dir,
                                                IMAGE_FILTER)
        if file_name:
            i = QMediaMetaData.CoverArtImage.value
            self.m_metaDataFields[i].setText(file_name[0])
