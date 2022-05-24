# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the widgets/layouts/borderlayout example from Qt v5.x"""

from dataclasses import dataclass
from enum import IntEnum, auto

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QLayout,
    QLayoutItem,
    QTextBrowser,
    QWidget,
    QWidgetItem,
)
import sys


class Position(IntEnum):
    West = auto()
    North = auto()
    South = auto()
    East = auto()
    Center = auto()


class SizeType(IntEnum):
    MinimumSize = auto()
    SizeHint = auto()


@dataclass
class ItemWrapper:
    item: QLayoutItem
    position: Position


class BorderLayout(QLayout):
    def __init__(self, parent=None, spacing: int = -1):
        super().__init__(parent)

        self._list: list[ItemWrapper] = []

        self.setSpacing(spacing)

        if parent is not None:
            self.setParent(parent)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QLayoutItem):
        self.add(item, Position.West)

    def addWidget(self, widget: QWidget, position: Position):
        self.add(QWidgetItem(widget), position)

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self) -> bool:
        return False

    def count(self) -> int:
        return len(self._list)

    def itemAt(self, index: int) -> QLayoutItem:
        if index < len(self._list):
            wrapper: ItemWrapper = self._list[index]
            return wrapper.item
        return None

    def minimumSize(self) -> QSize:
        return self.calculate_size(SizeType.MinimumSize)

    def setGeometry(self, rect: QRect):
        center: ItemWrapper = None
        east_width = 0
        west_width = 0
        north_height = 0
        south_height = 0

        super().setGeometry(rect)

        for wrapper in self._list:
            item: QLayoutItem = wrapper.item
            position: Position = wrapper.position

            if position == Position.North:
                item.setGeometry(
                    QRect(
                        rect.x(), north_height, rect.width(), item.sizeHint().height()
                    )
                )

                north_height += item.geometry().height() + self.spacing()

            elif position == Position.South:
                item.setGeometry(
                    QRect(
                        item.geometry().x(),
                        item.geometry().y(),
                        rect.width(),
                        item.sizeHint().height(),
                    )
                )

                south_height += item.geometry().height() + self.spacing()

                item.setGeometry(
                    QRect(
                        rect.x(),
                        rect.y() + rect.height() - south_height + self.spacing(),
                        item.geometry().width(),
                        item.geometry().height(),
                    )
                )
            elif position == Position.Center:
                center = wrapper

        center_height = rect.height() - north_height - south_height

        for wrapper in self._list:
            item: QLayoutItem = wrapper.item
            position: Position = wrapper.position

            if position == Position.West:
                item.setGeometry(
                    QRect(
                        rect.x() + west_width,
                        north_height,
                        item.sizeHint().width(),
                        center_height,
                    )
                )

                west_width += item.geometry().width() + self.spacing()

            elif position == Position.East:
                item.setGeometry(
                    QRect(
                        item.geometry().x(),
                        item.geometry().y(),
                        item.sizeHint().width(),
                        center_height,
                    )
                )

                east_width += item.geometry().width() + self.spacing()

                item.setGeometry(
                    QRect(
                        rect.x() + rect.width() - east_width + self.spacing(),
                        north_height,
                        item.geometry().width(),
                        item.geometry().height(),
                    )
                )

        if center:
            center.item.setGeometry(
                QRect(
                    west_width,
                    north_height,
                    rect.width() - east_width - west_width,
                    center_height,
                )
            )

    def sizeHint(self) -> QSize:
        return self.calculate_size(SizeType.SizeHint)

    def takeAt(self, index: int):
        if 0 <= index < len(self._list):
            layout_struct: ItemWrapper = self._list.pop(index)
            return layout_struct.item
        return None

    def add(self, item: QLayoutItem, position: Position):
        self._list.append(ItemWrapper(item, position))

    def calculate_size(self, size_type: SizeType):
        total_size = QSize()

        for wrapper in self._list:
            position = wrapper.position

            item_size: QSize
            if size_type == SizeType.MinimumSize:
                item_size = wrapper.item.minimumSize()
            else:
                item_size = wrapper.item.sizeHint()

            if position in (Position.North, Position.South, Position.Center):
                total_size.setHeight(total_size.height() + item_size.height())

            if position in (Position.West, Position.East, Position.Center):
                total_size.setWidth(total_size.width() + item_size.width())

        return total_size


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.central_widget = QTextBrowser()
        self.central_widget.setPlainText("Central widget")

        border_layout = BorderLayout()
        border_layout.addWidget(self.central_widget, Position.Center)

        label_north = self.create_label("North")
        border_layout.addWidget(label_north, Position.North)

        label_west = self.create_label("West")
        border_layout.addWidget(label_west, Position.West)

        label_east1 = self.create_label("East 1")
        border_layout.addWidget(label_east1, Position.East)

        label_east2 = self.create_label("East 2")
        border_layout.addWidget(label_east2, Position.East)

        label_south = self.create_label("South")
        border_layout.addWidget(label_south, Position.South)

        self.setLayout(border_layout)

        self.setWindowTitle("Border Layout")

    @staticmethod
    def create_label(text: str):
        label = QLabel(text)
        label.setFrameStyle(QFrame.Box | QFrame.Raised)
        return label


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
