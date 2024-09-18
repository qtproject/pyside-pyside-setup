# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import copy
from PySide6.QtSql import QSqlRelationalDelegate
from PySide6.QtWidgets import QSpinBox, QStyle
from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import QEvent, QSize, Qt


class BookDelegate(QSqlRelationalDelegate):
    """Books delegate to rate the books"""

    def __init__(self, parent=None):
        QSqlRelationalDelegate.__init__(self, parent)
        self.star = QPixmap(":/images/star.svg")
        self.star_filled = QPixmap(":/images/star-filled.svg")

    def paint(self, painter, option, index):
        """ Paint the items in the table.

            If the item referred to by <index> is a StarRating, we
            handle the painting ourselves. For the other items, we
            let the base class handle the painting as usual.

            In a polished application, we'd use a better check than
            the column number to find out if we needed to paint the
            stars, but it works for the purposes of this example.
        """
        if index.column() != 5:
            # Since we draw the grid ourselves:
            opt = copy.copy(option)
            opt.rect = option.rect.adjusted(0, 0, -1, -1)
            QSqlRelationalDelegate.paint(self, painter, opt, index)
        else:
            model = index.model()
            if option.state & QStyle.State_Enabled:
                if option.state & QStyle.State_Active:
                    color_group = QPalette.Normal
                else:
                    color_group = QPalette.Inactive
            else:
                color_group = QPalette.Disabled

            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect,
                                 option.palette.color(color_group, QPalette.Highlight))
            rating = model.data(index, Qt.ItemDataRole.DisplayRole)
            width = self.star.width()
            height = self.star.height()
            x = option.rect.x()
            y = option.rect.y() + (option.rect.height() / 2) - (height / 2)
            for i in range(5):
                if i < rating:
                    painter.drawPixmap(x, y, self.star_filled)
                else:
                    painter.drawPixmap(x, y, self.star)
                x += width

        pen = painter.pen()
        painter.setPen(option.palette.color(QPalette.Mid))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
        painter.setPen(pen)

    def sizeHint(self, option, index):
        """ Returns the size needed to display the item in a QSize object. """
        if index.column() == 5:
            size_hint = QSize(5 * self.star.width(), self.star.height()) + QSize(1, 1)
            return size_hint
        # Since we draw the grid ourselves:
        return QSqlRelationalDelegate.sizeHint(self, option, index) + QSize(1, 1)

    def editorEvent(self, event, model, option, index):
        if index.column() != 5:
            return False

        if event.type() == QEvent.MouseButtonPress:
            mouse_pos = event.position()
            new_stars = int(0.7 + (mouse_pos.x() - option.rect.x()) / self.star.width())
            stars = max(0, min(new_stars, 5))
            model.setData(index, stars)
            # So that the selection can change
            return False

        return True

    def createEditor(self, parent, option, index):
        if index.column() != 4:
            return QSqlRelationalDelegate.createEditor(self, parent, option, index)

        # For editing the year, return a spinbox with a range from -1000 to 2100.
        spinbox = QSpinBox(parent)
        spinbox.setFrame(False)
        spinbox.setMaximum(2100)
        spinbox.setMinimum(-1000)
        return spinbox
