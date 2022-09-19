# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QSizeF, Qt
from PySide6.QtWidgets import (QApplication, QGraphicsAnchorLayout,
                               QGraphicsProxyWidget, QGraphicsScene,
                               QGraphicsView, QGraphicsWidget,
                               QPushButton, QSizePolicy)


def create_item(minimum, preferred, maximum, name):
    w = QGraphicsProxyWidget()

    w.setWidget(QPushButton(name))
    w.setMinimumSize(minimum)
    w.setPreferredSize(preferred)
    w.setMaximumSize(maximum)
    w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    return w


if __name__ == '__main__':
    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 800, 480)

    min_size = QSizeF(30, 100)
    pref_size = QSizeF(210, 100)
    max_size = QSizeF(300, 100)

    a = create_item(min_size, pref_size, max_size, "A")
    b = create_item(min_size, pref_size, max_size, "B")
    c = create_item(min_size, pref_size, max_size, "C")
    d = create_item(min_size, pref_size, max_size, "D")
    e = create_item(min_size, pref_size, max_size, "E")
    f = create_item(QSizeF(30, 50), QSizeF(150, 50), max_size, "F")
    g = create_item(QSizeF(30, 50), QSizeF(30, 100), max_size, "G")

    l = QGraphicsAnchorLayout()
    l.setSpacing(0)

    w = QGraphicsWidget(None, Qt.Window)
    w.setPos(20, 20)
    w.setLayout(l)

    # Vertical.
    l.addAnchor(a, Qt.AnchorTop, l, Qt.AnchorTop)
    l.addAnchor(b, Qt.AnchorTop, l, Qt.AnchorTop)

    l.addAnchor(c, Qt.AnchorTop, a, Qt.AnchorBottom)
    l.addAnchor(c, Qt.AnchorTop, b, Qt.AnchorBottom)
    l.addAnchor(c, Qt.AnchorBottom, d, Qt.AnchorTop)
    l.addAnchor(c, Qt.AnchorBottom, e, Qt.AnchorTop)

    l.addAnchor(d, Qt.AnchorBottom, l, Qt.AnchorBottom)
    l.addAnchor(e, Qt.AnchorBottom, l, Qt.AnchorBottom)

    l.addAnchor(c, Qt.AnchorTop, f, Qt.AnchorTop)
    l.addAnchor(c, Qt.AnchorVerticalCenter, f, Qt.AnchorBottom)
    l.addAnchor(f, Qt.AnchorBottom, g, Qt.AnchorTop)
    l.addAnchor(c, Qt.AnchorBottom, g, Qt.AnchorBottom)

    # Horizontal.
    l.addAnchor(l, Qt.AnchorLeft, a, Qt.AnchorLeft)
    l.addAnchor(l, Qt.AnchorLeft, d, Qt.AnchorLeft)
    l.addAnchor(a, Qt.AnchorRight, b, Qt.AnchorLeft)

    l.addAnchor(a, Qt.AnchorRight, c, Qt.AnchorLeft)
    l.addAnchor(c, Qt.AnchorRight, e, Qt.AnchorLeft)

    l.addAnchor(b, Qt.AnchorRight, l, Qt.AnchorRight)
    l.addAnchor(e, Qt.AnchorRight, l, Qt.AnchorRight)
    l.addAnchor(d, Qt.AnchorRight, e, Qt.AnchorLeft)

    l.addAnchor(l, Qt.AnchorLeft, f, Qt.AnchorLeft)
    l.addAnchor(l, Qt.AnchorLeft, g, Qt.AnchorLeft)
    l.addAnchor(f, Qt.AnchorRight, g, Qt.AnchorRight)

    scene.addItem(w)
    scene.setBackgroundBrush(Qt.darkGreen)

    view = QGraphicsView(scene)
    view.show()

    sys.exit(app.exec())
