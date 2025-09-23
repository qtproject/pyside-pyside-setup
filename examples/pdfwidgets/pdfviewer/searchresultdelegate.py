# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QStyle, QStyledItemDelegate
from PySide6.QtPdf import QPdfSearchModel


class SearchResultDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        displayText = index.data()
        boldBegin = displayText.find("<b>") + 3
        boldEnd = displayText.find("</b>", boldBegin)
        if boldBegin >= 3 and boldEnd > boldBegin:
            page = index.data(QPdfSearchModel.Role.Page.value)
            pageLabel = f"Page {page}: "
            boldText = displayText[boldBegin:boldEnd]
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
            defaultFont = painter.font()
            fm = painter.fontMetrics()
            pageLabelWidth = fm.horizontalAdvance(pageLabel)
            yOffset = (option.rect.height() - fm.height()) / 2 + fm.ascent()
            painter.drawText(0, option.rect.y() + yOffset, pageLabel)
            boldFont = QFont(defaultFont)
            boldFont.setBold(True)
            boldWidth = QFontMetrics(boldFont).horizontalAdvance(boldText)
            prefixSuffixWidth = (option.rect.width() - pageLabelWidth - boldWidth) / 2
            painter.setFont(boldFont)
            painter.drawText(pageLabelWidth + prefixSuffixWidth, option.rect.y() + yOffset,
                             boldText)
            painter.setFont(defaultFont)
            suffix = fm.elidedText(displayText[boldEnd + 4:],
                                   Qt.TextElideMode.ElideRight, prefixSuffixWidth)
            painter.drawText(pageLabelWidth + prefixSuffixWidth + boldWidth,
                             option.rect.y() + yOffset, suffix)
            prefix = fm.elidedText(displayText[0:boldBegin - 3],
                                   Qt.TextElideMode.ElideLeft, prefixSuffixWidth)
            painter.drawText(pageLabelWidth + prefixSuffixWidth - fm.horizontalAdvance(prefix),
                             option.rect.y() + yOffset, prefix)
        else:
            super().paint(painter, option, index)
