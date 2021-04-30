
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

import sys

from PySide6.QtCore import QSizeF, Qt
from PySide6.QtWidgets import (QApplication, QGraphicsAnchorLayout,
                               QGraphicsProxyWidget, QGraphicsScene,
                               QGraphicsView, QGraphicsWidget,
                               QPushButton, QSizePolicy, QWidget)


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
