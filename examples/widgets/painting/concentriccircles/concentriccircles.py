# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the widgets/painting/concentriccircles example from Qt v5.x, originating from PyQt"""

from PySide6.QtCore import QRect, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPalette, QPen
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
        QSizePolicy, QWidget)


class CircleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._float_based = False
        self.antialiased = False
        self._frame_no = 0

        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_float_based(self, floatBased):
        self._float_based = floatBased
        self.update()

    def set_antialiased(self, antialiased):
        self.antialiased = antialiased
        self.update()

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(180, 180)

    def next_animation_frame(self):
        self._frame_no += 1
        self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing, self.antialiased)
            painter.translate(self.width() / 2, self.height() / 2)

            for diameter in range(0, 256, 9):
                delta = abs((self._frame_no % 128) - diameter / 2)
                alpha = 255 - (delta * delta) / 4 - diameter
                if alpha > 0:
                    painter.setPen(QPen(QColor(0, diameter / 2, 127, alpha), 3))

                    if self._float_based:
                        painter.drawEllipse(QRectF(-diameter / 2.0,
                                -diameter / 2.0, diameter, diameter))
                    else:
                        painter.drawEllipse(QRect(-diameter / 2,
                                -diameter / 2, diameter, diameter))


class Window(QWidget):
    def __init__(self):
        super().__init__()

        aliased_label = self.create_label("Aliased")
        antialiased_label = self.create_label("Antialiased")
        int_label = self.create_label("Int")
        float_label = self.create_label("Float")

        layout = QGridLayout()
        layout.addWidget(aliased_label, 0, 1)
        layout.addWidget(antialiased_label, 0, 2)
        layout.addWidget(int_label, 1, 0)
        layout.addWidget(float_label, 2, 0)

        timer = QTimer(self)

        for i in range(2):
            for j in range(2):
                w = CircleWidget()
                w.set_antialiased(j != 0)
                w.set_float_based(i != 0)

                timer.timeout.connect(w.next_animation_frame)

                layout.addWidget(w, i + 1, j + 1)

        timer.start(100)
        self.setLayout(layout)

        self.setWindowTitle("Concentric Circles")

    def create_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setMargin(2)
        label.setFrameStyle(QFrame.Box | QFrame.Sunken)
        return label


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
