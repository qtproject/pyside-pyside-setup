
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

"""PySide6 port of the widgets/richtext/textobject example from Qt v5.x"""

import os
from pathlib import Path
import sys

from PySide6.QtCore import QFile, QIODevice, QObject, QSizeF, Qt
from PySide6.QtGui import (QTextCharFormat, QTextFormat, QTextObjectInterface,
                           QPyTextObject)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget)
from PySide6.QtSvg import QSvgRenderer


SVG_TEXT_FORMAT = QTextFormat.UserObject + 1


SVG_DATA = 1


class SvgTextObject(QPyTextObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def intrinsicSize(self, doc, posInDocument, format):
        renderer = QSvgRenderer(format.property(SVG_DATA))
        size = renderer.defaultSize()

        if size.height() > 25:
            size *= 25.0 / size.height()

        return QSizeF(size)

    def drawObject(self, painter, rect, doc, posInDocument, format):
        renderer = QSvgRenderer(format.property(SVG_DATA))
        renderer.render(painter, rect)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_gui()
        self.setup_text_object()

        self.setWindowTitle(self.tr("Text Object Example"))

    def insert_text_object(self):
        file_name = self._file_name_line_edit.text()
        file = QFile(file_name)

        if not file.open(QIODevice.ReadOnly):
            reason = file.errorString()
            message = f"Could not open '{file_name}': {reason}"
            QMessageBox.warning(self, "Error Opening File", message)

        svg_data = file.readAll()

        svg_char_format = QTextCharFormat()
        svg_char_format.setObjectType(SVG_TEXT_FORMAT)
        svg_char_format.setProperty(SVG_DATA, svg_data)

        cursor = self._text_edit.textCursor()
        cursor.insertText(chr(0xfffc), svg_char_format)
        self._text_edit.setTextCursor(cursor)

    def setup_text_object(self):
        svg_interface = SvgTextObject(self)
        doc_layout = self._text_edit.document().documentLayout()
        doc_layout.registerHandler(SVG_TEXT_FORMAT, svg_interface)

    def setup_gui(self):
        file_name_label = QLabel(self.tr("Svg File Name:"))
        self._file_name_line_edit = QLineEdit()
        self._file_name_line_edit.setClearButtonEnabled(True)
        insert_text_object_button = QPushButton(self.tr("Insert Image"))

        file = os.fspath(Path(__file__).resolve().parent / 'files' / 'heart.svg')
        self._file_name_line_edit.setText(file)
        insert_text_object_button.clicked.connect(self.insert_text_object)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(file_name_label)
        bottom_layout.addWidget(self._file_name_line_edit)
        bottom_layout.addWidget(insert_text_object_button)

        self._text_edit = QTextEdit()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._text_edit)
        main_layout.addLayout(bottom_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
