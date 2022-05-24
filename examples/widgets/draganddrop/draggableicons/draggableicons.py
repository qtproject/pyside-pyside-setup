# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from pathlib import Path
import sys

from PySide6.QtCore import QByteArray, QDataStream, QIODevice, QMimeData, QPoint, Qt
from PySide6.QtGui import QColor, QDrag, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QWidget


class DragWidget(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAcceptDrops(True)

        path = Path(__file__).resolve().parent

        boat_icon = QLabel(self)
        boat_icon.setPixmap(QPixmap(path / "images" / "boat.png"))
        boat_icon.move(10, 10)
        boat_icon.show()
        boat_icon.setAttribute(Qt.WA_DeleteOnClose)

        car_icon = QLabel(self)
        car_icon.setPixmap(QPixmap(path / "images" / "car.png"))
        car_icon.move(100, 10)
        car_icon.show()
        car_icon.setAttribute(Qt.WA_DeleteOnClose)

        house_icon = QLabel(self)
        house_icon.setPixmap(QPixmap(path / "images" / "house.png"))
        house_icon.move(10, 80)
        house_icon.show()
        house_icon.setAttribute(Qt.WA_DeleteOnClose)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-dnditem_data"):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-dnditem_data"):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-dnditem_data"):
            item_data: QByteArray = event.mimeData().data("application/x-dnditem_data")
            data_stream = QDataStream(item_data, QIODevice.ReadOnly)

            pixmap = QPixmap()
            offset = QPoint()

            data_stream >> pixmap >> offset

            new_icon = QLabel(self)
            new_icon.setPixmap(pixmap)
            new_icon.move(event.position().toPoint() - offset)
            new_icon.show()
            new_icon.setAttribute(Qt.WA_DeleteOnClose)

            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        child: QLabel = self.childAt(event.position().toPoint())
        if not child:
            return

        pixmap = child.pixmap()

        item_data = QByteArray()
        data_stream = QDataStream(item_data, QIODevice.WriteOnly)

        data_stream << pixmap << QPoint(event.position().toPoint() - child.pos())

        mime_data = QMimeData()
        mime_data.setData("application/x-dnditem_data", item_data)

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint() - child.pos())

        # .copy() is important: python is different than c++ in this case
        temp_pixmap = pixmap.copy()
        with QPainter(temp_pixmap) as painter:
            painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))

        child.setPixmap(temp_pixmap)

        if drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_widget = QWidget()
    horizontal_layout = QHBoxLayout(main_widget)
    horizontal_layout.addWidget(DragWidget(main_widget))
    horizontal_layout.addWidget(DragWidget(main_widget))

    main_widget.setWindowTitle("Draggable Icons")
    main_widget.show()

    sys.exit(app.exec())
