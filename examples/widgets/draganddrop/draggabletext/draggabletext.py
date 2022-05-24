# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the widgets/draganddrop/draggabletext example from Qt v5.x, originating from PyQt"""

from PySide6.QtCore import QFile, QIODevice, QMimeData, QPoint, Qt, QTextStream
from PySide6.QtGui import QDrag, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QWidget

import draggabletext_rc


class DragLabel(QLabel):
    def __init__(self, text, parent):
        super().__init__(text, parent)

        self.setAutoFillBackground(True)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)

    def mousePressEvent(self, event):
        hot_spot = event.position().toPoint()

        mime_data = QMimeData()
        mime_data.setText(self.text())
        hx = hot_spot.x()
        hy = hot_spot.y()
        mime_data.setData('application/x-hotspot', f'{hx} {hy}'.encode('utf-8'))

        pixmap = QPixmap(self.size())
        self.render(pixmap)

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hot_spot)

        drop_action = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)

        if drop_action == Qt.MoveAction:
            self.close()
            self.update()


class DragWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        dictionary_file = QFile(':/dictionary/words.txt')
        dictionary_file.open(QIODevice.ReadOnly)

        x = 5
        y = 5

        for word in QTextStream(dictionary_file).readAll().split():
            word_label = DragLabel(word, self)
            word_label.move(x, y)
            word_label.show()
            x += word_label.width() + 2
            if x >= 195:
                x = 5
                y += word_label.height() + 2

        new_palette = self.palette()
        new_palette.setColor(QPalette.Window, Qt.white)
        self.setPalette(new_palette)

        self.setAcceptDrops(True)
        self.setMinimumSize(400, max(200, y))
        self.setWindowTitle("Draggable Text")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.source() in self.children():
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            mime = event.mimeData()
            pieces = mime.text().split()
            position = event.position().toPoint()
            hot_spot = QPoint()

            hot_spot_pos = mime.data('application/x-hotspot').split(' ')
            if len(hot_spot_pos) == 2:
                hot_spot.setX(hot_spot_pos[0].toInt()[0])
                hot_spot.setY(hot_spot_pos[1].toInt()[0])

            for piece in pieces:
                new_label = DragLabel(piece, self)
                new_label.move(position - hot_spot)
                new_label.show()

                position += QPoint(new_label.width(), 0)

            if event.source() in self.children():
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = DragWidget()
    window.show()
    sys.exit(app.exec())
