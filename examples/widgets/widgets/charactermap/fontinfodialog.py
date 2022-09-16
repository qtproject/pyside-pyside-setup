# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt, qVersion, qFuzzyCompare
from PySide6.QtGui import QGuiApplication, QFontDatabase
from PySide6.QtWidgets import (QDialog, QDialogButtonBox,
                               QPlainTextEdit, QVBoxLayout)


def _format_font(font):
    family = font.family()
    size = font.pointSizeF()
    return f"{family}, {size}pt"


class FontInfoDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        main_layout = QVBoxLayout(self)
        text_edit = QPlainTextEdit(self.text(), self)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        main_layout.addWidget(text_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Close, self)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def text(self):
        default_font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        title_font = QFontDatabase.systemFont(QFontDatabase.TitleFont)
        smallest_readable_font = QFontDatabase.systemFont(QFontDatabase.SmallestReadableFont)

        v = qVersion()
        platform = QGuiApplication.platformName()
        dpi = self.logicalDpiX()
        dpr = self.devicePixelRatio()
        text = f"Qt {v} on {platform}, {dpi}DPI"
        if not qFuzzyCompare(dpr, float(1)):
            text += f", device pixel ratio: {dpr}"
        text += ("\n\nDefault font : " + _format_font(default_font)
                 + "\nFixed font : " + _format_font(fixed_font)
                 + "\nTitle font : " + _format_font(title_font)
                 + "\nSmallest font: " + _format_font(smallest_readable_font))
        return text
