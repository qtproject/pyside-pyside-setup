
#############################################################################
##
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

from pathlib import Path
import sys
from PySide6.QtCore import QObject, QUrl, Property, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

# This example illustrates exposing a list of QObjects as a model in QML

class DataObject(QObject):

    nameChanged = Signal()
    colorChanged = Signal()

    def __init__(self, name, color, parent=None):
        super().__init__(parent)
        self._name = name
        self._color = color

    def name(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            self._name = name
            nameChanged.emit()

    def color(self):
        return self._color

    def setColor(self, color):
        if color != self._color:
            self._color = color
            colorChanged.emit()


    name = Property(str, name, setName, notify=nameChanged)
    color = Property(str, color, setColor, notify=colorChanged)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    dataList = [DataObject("Item 1", "red"),
                DataObject("Item 2", "green"),
                DataObject("Item 3", "blue"),
                DataObject("Item 4", "yellow")]

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setInitialProperties({"model": dataList})

    qml_file = Path(__file__).parent / "view.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))
    view.show()

    r = app.exec()
    del view
    sys.exit(r)
