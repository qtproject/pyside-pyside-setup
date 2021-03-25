
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
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

from PySide6 import QtCore, QtGui, QtWidgets, QtSvg


class SvgTextObject(QtCore.QObject, QtGui.QTextObjectInterface):

    def intrinsicSize(self, doc, posInDocument, format):
        renderer = QtSvg.QSvgRenderer(format.property(Window.svg_data).toByteArray())
        size = renderer.defaultSize()

        if size.height() > 25:
            size *= 25.0 / size.height()

        return QtCore.QSizeF(size)

    def drawObject(self, painter, rect, doc, posInDocument, format):
        renderer = QtSvg.QSvgRenderer(format.property(Window.svg_data).toByteArray())
        renderer.render(painter, rect)


class Window(QtWidgets.QWidget):

    svg_text_format = QtGui.QTextFormat.UserObject + 1

    svg_data = 1

    def __init__(self):
        super(Window, self).__init__()

        self.setup_gui()
        self.setup_text_object()

        self.setWindowTitle(self.tr("Text Object Example"))

    def insert_text_object(self):
        file_name = self._file_name_line_edit.text()
        file = QtCore.QFile(file_name)

        if not file.open(QtCore.QIODevice.ReadOnly):
            QtWidgets.QMessageBox.warning(self, self.tr("Error Opening File"),
                    self.tr("Could not open '%1'").arg(file_name))

        svg_data = file.readAll()

        svg_char_format = QtGui.QTextCharFormat()
        svg_char_format.setObjectType(Window.svg_text_format)
        svg_char_format.setProperty(Window.svg_data, svg_data)

        cursor = self._text_edit.textCursor()
        cursor.insertText(u"\uFFFD", svg_char_format)
        self._text_edit.setTextCursor(cursor)

    def setup_text_object(self):
        svg_interface = SvgTextObject(self)
        self._text_edit.document().documentLayout().registerHandler(Window.svg_text_format, svg_interface)

    def setup_gui(self):
        file_name_label = QtWidgets.QLabel(self.tr("Svg File Name:"))
        self._file_name_line_edit = QtWidgets.QLineEdit()
        insert_text_object_button = QtWidgets.QPushButton(self.tr("Insert Image"))

        self._file_name_line_edit.setText('./files/heart.svg')
        QtCore.QObject.connect(insert_text_object_button, QtCore.SIGNAL('clicked()'), self.insert_text_object)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(file_name_label)
        bottom_layout.addWidget(self._file_name_line_edit)
        bottom_layout.addWidget(insert_text_object_button)

        self._text_edit = QtWidgets.QTextEdit()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._text_edit)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
