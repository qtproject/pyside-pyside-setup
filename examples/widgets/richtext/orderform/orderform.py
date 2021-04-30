
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

"""PySide6 port of the widgets/richtext/orderform example from Qt v5.x"""

import sys

from PySide6.QtCore import QDate, Qt, Signal, Slot
from PySide6.QtGui import (QFont, QTextCharFormat, QTextCursor,
                           QTextFrameFormat, QTextLength, QTextTableFormat)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog,
                               QDialogButtonBox, QGridLayout, QLabel,
                               QLineEdit, QMainWindow, QMenu, QMessageBox,
                               QTableWidget, QTableWidgetItem, QTabWidget,
                               QTextEdit, QWidget)
from PySide6.QtPrintSupport import QAbstractPrintDialog, QPrintDialog, QPrinter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        file_menu = QMenu("&File", self)
        new_action = file_menu.addAction("&New...")
        new_action.setShortcut("Ctrl+N")
        self._print_action = file_menu.addAction("&Print...", self.print_file)
        self._print_action.setShortcut("Ctrl+P")
        self._print_action.setEnabled(False)
        quit_action = file_menu.addAction("E&xit")
        quit_action.setShortcut("Ctrl+Q")
        self.menuBar().addMenu(file_menu)

        self.letters = QTabWidget()

        new_action.triggered.connect(self.open_dialog)
        quit_action.triggered.connect(self.close)

        self.setCentralWidget(self.letters)
        self.setWindowTitle("Order Form")

    def create_letter(self, name, address, orderItems, sendOffers):
        editor = QTextEdit()
        tab_index = self.letters.addTab(editor, name)
        self.letters.setCurrentIndex(tab_index)

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        top_frame = cursor.currentFrame()
        top_frame_format = top_frame.frameFormat()
        top_frame_format.setPadding(16)
        top_frame.setFrameFormat(top_frame_format)

        text_format = QTextCharFormat()
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)

        reference_frame_format = QTextFrameFormat()
        reference_frame_format.setBorder(1)
        reference_frame_format.setPadding(8)
        reference_frame_format.setPosition(QTextFrameFormat.FloatRight)
        reference_frame_format.setWidth(QTextLength(QTextLength.PercentageLength, 40))
        cursor.insertFrame(reference_frame_format)

        cursor.insertText("A company", bold_format)
        cursor.insertBlock()
        cursor.insertText("321 City Street")
        cursor.insertBlock()
        cursor.insertText("Industry Park")
        cursor.insertBlock()
        cursor.insertText("Another country")

        cursor.setPosition(top_frame.lastPosition())

        cursor.insertText(name, text_format)
        for line in address.split("\n"):
            cursor.insertBlock()
            cursor.insertText(line)

        cursor.insertBlock()
        cursor.insertBlock()

        date = QDate.currentDate()
        date_str = date.toString('d MMMM yyyy')
        cursor.insertText(f"Date: {date_str}", text_format)
        cursor.insertBlock()

        body_frame_format = QTextFrameFormat()
        body_frame_format.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        cursor.insertFrame(body_frame_format)

        cursor.insertText("I would like to place an order for the following "
                "items:", text_format)
        cursor.insertBlock()
        cursor.insertBlock()

        order_table_format = QTextTableFormat()
        order_table_format.setAlignment(Qt.AlignHCenter)
        order_table = cursor.insertTable(1, 2, order_table_format)

        order_frame_format = cursor.currentFrame().frameFormat()
        order_frame_format.setBorder(1)
        cursor.currentFrame().setFrameFormat(order_frame_format)

        cursor = order_table.cellAt(0, 0).firstCursorPosition()
        cursor.insertText("Product", bold_format)
        cursor = order_table.cellAt(0, 1).firstCursorPosition()
        cursor.insertText("Quantity", bold_format)

        for text, quantity in orderItems:
            row = order_table.rows()

            order_table.insertRows(row, 1)
            cursor = order_table.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(text, text_format)
            cursor = order_table.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(str(quantity), text_format)

        cursor.setPosition(top_frame.lastPosition())

        cursor.insertBlock()

        cursor.insertText("Please update my records to take account of the "
                "following privacy information:")
        cursor.insertBlock()

        offers_table = cursor.insertTable(2, 2)

        cursor = offers_table.cellAt(0, 1).firstCursorPosition()
        cursor.insertText("I want to receive more information about your "
                "company's products and special offers.", text_format)
        cursor = offers_table.cellAt(1, 1).firstCursorPosition()
        cursor.insertText("I do not want to receive any promotional "
                "information from your company.", text_format)

        if sendOffers:
            cursor = offers_table.cellAt(0, 0).firstCursorPosition()
        else:
            cursor = offers_table.cellAt(1, 0).firstCursorPosition()

        cursor.insertText('X', bold_format)

        cursor.setPosition(top_frame.lastPosition())
        cursor.insertBlock()
        cursor.insertText("Sincerely,", text_format)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(name)

        self._print_action.setEnabled(True)

    def create_sample(self):
        dialog = DetailsDialog('Dialog with default values', self)
        self.create_letter('Mr Smith',
                '12 High Street\nSmall Town\nThis country',
                dialog.order_items(), True)

    def open_dialog(self):
        dialog = DetailsDialog("Enter Customer Details", self)

        if dialog.exec() == QDialog.Accepted:
            self.create_letter(dialog.sender_name(), dialog.sender_address(),
                    dialog.order_items(), dialog.send_offers())

    def print_file(self):
        editor = self.letters.currentWidget()
        printer = QPrinter()

        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Print Document")

        if editor.textCursor().hasSelection():
            dialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)

        if dialog.exec() != QDialog.Accepted:
            return

        editor.print_(printer)


class DetailsDialog(QDialog):
    def __init__(self, title, parent):
        super().__init__(parent)

        self.items = ("T-shirt", "Badge", "Reference book", "Coffee cup")

        name_label = QLabel("Name:")
        address_label = QLabel("Address:")
        address_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._name_edit = QLineEdit()
        self._address_edit = QTextEdit()
        self._offers_check_box = QCheckBox("Send information about "
                "products and special offers:")

        self.setup_items_table()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.verify)
        button_box.rejected.connect(self.reject)

        main_layout = QGridLayout(self)
        main_layout.addWidget(name_label, 0, 0)
        main_layout.addWidget(self._name_edit, 0, 1)
        main_layout.addWidget(address_label, 1, 0)
        main_layout.addWidget(self._address_edit, 1, 1)
        main_layout.addWidget(self._items_table, 0, 2, 2, 1)
        main_layout.addWidget(self._offers_check_box, 2, 1, 1, 2)
        main_layout.addWidget(button_box, 3, 0, 1, 3)

        self.setWindowTitle(title)

    def setup_items_table(self):
        self._items_table = QTableWidget(len(self.items), 2)

        for row, item in enumerate(self.items):
            name = QTableWidgetItem(item)
            name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._items_table.setItem(row, 0, name)
            quantity = QTableWidgetItem('1')
            self._items_table.setItem(row, 1, quantity)

    def order_items(self):
        order_list = []

        for row in range(len(self.items)):
            text = self._items_table.item(row, 0).text()
            quantity = int(self._items_table.item(row, 1).data(Qt.DisplayRole))
            order_list.append((text, max(0, quantity)))

        return order_list

    def sender_name(self):
        return self._name_edit.text()

    def sender_address(self):
        return self._address_edit.toPlainText()

    def send_offers(self):
        return self._offers_check_box.isChecked()

    def verify(self):
        if self._name_edit.text() and self._address_edit.toPlainText():
            self.accept()
            return

        answer = QMessageBox.warning(self, "Incomplete Form",
                "The form does not contain all the necessary information.\n"
                "Do you want to discard it?",
                QMessageBox.Yes, QMessageBox.No)

        if answer == QMessageBox.Yes:
            self.reject()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    window.create_sample()
    sys.exit(app.exec())
