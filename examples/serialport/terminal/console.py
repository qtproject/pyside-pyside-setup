#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QPlainTextEdit


UNHANDLED_KEYS = [Qt.Key_Backspace, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up,
                  Qt.Key_Down]


class Console(QPlainTextEdit):

    get_data = Signal(bytearray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_localEchoEnabled = False
        self.document().setMaximumBlockCount(100)
        p = self.palette()
        p.setColor(QPalette.Base, Qt.black)
        p.setColor(QPalette.Text, Qt.green)
        self.setPalette(p)

    @Slot(bytearray)
    def put_data(self, data):
        self.insertPlainText(data.decode("utf8"))
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())

    def set_local_echo_enabled(self, e):
        self.m_localEchoEnabled = e

    def keyPressEvent(self, e):
        key = e.key()
        if key not in UNHANDLED_KEYS:
            if self.m_localEchoEnabled:
                super().keyPressEvent(e)
            self.get_data.emit(e.text().encode())

    def mousePressEvent(self, e):
        self.setFocus()

    def mouseDoubleClickEvent(self, e):
        pass

    def contextMenuEvent(self, e):
        pass
