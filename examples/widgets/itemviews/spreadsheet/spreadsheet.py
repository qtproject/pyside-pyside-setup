# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QCoreApplication, Slot
from PySide6.QtGui import QAction, QBrush, QPixmap, QColor, QPainter
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog, QFontDialog,
                               QGroupBox, QHBoxLayout, QMainWindow, QLabel,
                               QLineEdit, QMessageBox, QPushButton, QToolBar,
                               QTableWidgetItem, QTableWidget, QVBoxLayout, QWidget)

from spreadsheetdelegate import SpreadSheetDelegate
from spreadsheetitem import SpreadSheetItem

from numbers import Number


class SpreadSheet(QMainWindow):
    def __init__(self, rows: Number, cols: Number, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._tool_bar = QToolBar(self)
        self._color_action = QAction()
        self._font_action = QAction()
        self._first_separator = QAction()
        self._cell_sum_action = QAction()
        self._cell_add_action = QAction()
        self._cell_sub_action = QAction()
        self._cell_mul_action = QAction()
        self._cell_div_action = QAction()
        self._second_separator = QAction()
        self._clear_action = QAction()
        self._about_spreadsheet = QAction()
        self._exit_action = QAction()

        # self._print_action = QAction()

        self._cell_label = QLabel(self._tool_bar)
        self._table = QTableWidget(rows, cols, self)
        self._formula_input = QLineEdit(self)

        self.addToolBar(self._tool_bar)

        self._cell_label.setMinimumSize(80, 0)

        self._tool_bar.addWidget(self._cell_label)
        self._tool_bar.addWidget(self._formula_input)

        self._table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        for c in range(cols):
            character = chr(ord('A') + c)
            self._table.setHorizontalHeaderItem(c, QTableWidgetItem(character))

        self._table.setItemPrototype(self._table.item(rows - 1, cols - 1))
        self._table.setItemDelegate(SpreadSheetDelegate())

        self.create_actions()
        self.update_color(None)
        self.setup_menu_bar()
        self.setup_contents()
        self.setup_context_menu()
        self.setCentralWidget(self._table)

        self.statusBar()
        self._table.currentItemChanged.connect(self.update_status)
        self._table.currentItemChanged.connect(self.update_color)
        self._table.currentItemChanged.connect(self.update_line_edit)
        self._table.itemChanged.connect(self.update_status)
        self._formula_input.returnPressed.connect(self.return_pressed)
        self._table.itemChanged.connect(self.update_line_edit)

        self.setWindowTitle("Spreadsheet")

    def create_actions(self) -> None:
        self._cell_sum_action = QAction("Sum", self)
        self._cell_sum_action.triggered.connect(self.action_sum)

        self._cell_add_action = QAction("&Add", self)
        self._cell_add_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Plus)
        self._cell_add_action.triggered.connect(self.action_add)

        self._cell_sub_action = QAction("&Subtract", self)
        self._cell_sub_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Minus)
        self._cell_sub_action.triggered.connect(self.action_subtract)

        self._cell_mul_action = QAction("&Multiply", self)
        self._cell_mul_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_multiply)
        self._cell_mul_action.triggered.connect(self.action_multiply)

        self._cell_div_action = QAction("&Divide", self)
        self._cell_div_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_division)
        self._cell_div_action.triggered.connect(self.action_divide)

        self._font_action = QAction("Font...", self)
        self._font_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_F)
        self._font_action.triggered.connect(self.select_font)

        self._color_action = QAction(QPixmap(16, 16), "Background &Color...", self)
        self._color_action.triggered.connect(self.select_color)

        self._clear_action = QAction("Clear", self)
        self._clear_action.setShortcut(Qt.Key.Key_Delete)
        self._clear_action.triggered.connect(self.clear)

        self._about_spreadsheet = QAction("About Spreadsheet", self)
        self._about_spreadsheet.triggered.connect(self.show_about)

        self._exit_action = QAction("E&xit", self)
        self._exit_action.triggered.connect(QCoreApplication.quit)

        self._first_separator = QAction(self)
        self._first_separator.setSeparator(True)

        self._second_separator = QAction(self)
        self._second_separator.setSeparator(True)

    def setup_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        # file_menu.addAction(self._print_action)
        file_menu.addAction(self._exit_action)

        cell_menu = self.menuBar().addMenu("&Cell")
        cell_menu.addAction(self._cell_add_action)
        cell_menu.addAction(self._cell_sub_action)
        cell_menu.addAction(self._cell_mul_action)
        cell_menu.addAction(self._cell_div_action)
        cell_menu.addAction(self._cell_sum_action)
        cell_menu.addSeparator()
        cell_menu.addAction(self._color_action)
        cell_menu.addAction(self._font_action)

        self.menuBar().addSeparator()

        about_menu = self.menuBar().addMenu("&Help")
        about_menu.addAction(self._about_spreadsheet)

    @Slot(QTableWidgetItem)
    def update_status(self, item: QTableWidgetItem) -> None:
        if item and item == self._table.currentItem():
            self.statusBar().showMessage(str(item.data(Qt.ItemDataRole.StatusTipRole)), 1000)
            self._cell_label.setText(
                "Cell: ({})".format(
                    SpreadSheetItem.encode_pos(self._table.row(item), self._table.column(item))
                )
            )

    @Slot(QTableWidgetItem)
    def update_color(self, item: QTableWidgetItem) -> None:
        pix = QPixmap(16, 16)
        col = QColor()
        if item:
            col = item.background().color()
        if not col.isValid():
            col = self.palette().base().color()

        pt = QPainter(pix)
        pt.fillRect(0, 0, 16, 16, col)

        lighter = col.lighter()
        pt.setPen(lighter)
        light_frame = [QPoint(0, 15), QPoint(0, 0), QPoint(15, 0)]
        pt.drawPolyline(light_frame)

        pt.setPen(col.darker())
        darkFrame = [QPoint(1, 15), QPoint(15, 15), QPoint(15, 1)]
        pt.drawPolyline(darkFrame)

        pt.end()

        self._color_action.setIcon(pix)

    @Slot(QTableWidgetItem)
    def update_line_edit(self, item: QTableWidgetItem) -> None:
        if item != self._table.currentItem():
            return
        if item:
            self._formula_input.setText(str(item.data(Qt.ItemDataRole.EditRole)))
        else:
            self._formula_input.clear()

    @Slot()
    def return_pressed(self) -> None:
        text = self._formula_input.text()
        row = self._table.currentRow()
        col = self._table.currentColumn()
        item = self._table.item(row, col)
        if not item:
            self._table.setItem(row, col, SpreadSheetItem(text))
        else:
            item.setData(Qt.ItemDataRole.EditRole, text)
        self._table.viewport().update()

    @Slot()
    def select_color(self) -> None:
        item = self._table.currentItem()
        col = item.background().color() if item else self._table.palette().base().color()
        col = QColorDialog.getColor(col, self)
        if not col.isValid():
            return

        selected = self._table.selectedItems()
        if not selected:
            return

        for i in selected:
            if i:
                i.setBackground(col)

        self.update_color(self._table.currentItem())

    @Slot()
    def select_font(self) -> None:
        selected = self._table.selectedItems()
        if not selected:
            return

        ok = False
        fnt = QFontDialog.getFont(ok, self.font(), self)

        if not ok:
            return
        for i in selected:
            if i:
                i.setFont(fnt)

    def run_input_dialog(self, title: str, c1Text: str, c2Text: str, opText: str,
                         outText: str, cell1: str, cell2: str, outCell: str) -> bool:
        rows, cols = [], []
        for c in range(self._table.columnCount()):
            cols.append(chr(ord('A') + c))
        for r in range(self._table.rowCount()):
            rows.append(str(1 + r))

        add_dialog = QDialog(self)
        add_dialog.setWindowTitle(title)

        group = QGroupBox(title, add_dialog)
        group.setMinimumSize(250, 100)

        cell1_label = QLabel(c1Text, group)
        cell1_row_input = QComboBox(group)
        c1_row, c1_col = SpreadSheetItem.decode_pos(cell1)
        cell1_row_input.addItems(rows)
        cell1_row_input.setCurrentIndex(c1_row)

        cell1_col_input = QComboBox(group)
        cell1_col_input.addItems(cols)
        cell1_col_input.setCurrentIndex(c1_col)

        operator_label = QLabel(opText, group)
        operator_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        cell2_label = QLabel(c2Text, group)
        cell2_row_input = QComboBox(group)
        c2_row, c2_col = SpreadSheetItem.decode_pos(cell2)
        cell2_row_input.addItems(rows)
        cell2_row_input.setCurrentIndex(c2_row)
        cell2_col_input = QComboBox(group)
        cell2_col_input.addItems(cols)
        cell2_col_input.setCurrentIndex(c2_col)

        equals_label = QLabel("=", group)
        equals_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        out_label = QLabel(outText, group)
        out_row_input = QComboBox(group)
        out_row, out_col = SpreadSheetItem.decode_pos(outCell)
        out_row_input.addItems(rows)
        out_row_input.setCurrentIndex(out_row)
        out_col_input = QComboBox(group)
        out_col_input.addItems(cols)
        out_col_input.setCurrentIndex(out_col)

        cancel_button = QPushButton("Cancel", add_dialog)
        cancel_button.clicked.connect(add_dialog.reject)

        ok_button = QPushButton("OK", add_dialog)
        ok_button.setDefault(True)
        ok_button.clicked.connect(add_dialog.accept)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(cancel_button)

        dialog_layout = QVBoxLayout(add_dialog)
        dialog_layout.addWidget(group)
        dialog_layout.addStretch(1)
        dialog_layout.addItem(buttons_layout)

        cell1_layout = QHBoxLayout()
        cell1_layout.addWidget(cell1_label)
        cell1_layout.addSpacing(10)
        cell1_layout.addWidget(cell1_col_input)
        cell1_layout.addSpacing(10)
        cell1_layout.addWidget(cell1_row_input)

        cell2_layout = QHBoxLayout()
        cell2_layout.addWidget(cell2_label)
        cell2_layout.addSpacing(10)
        cell2_layout.addWidget(cell2_col_input)
        cell2_layout.addSpacing(10)
        cell2_layout.addWidget(cell2_row_input)

        out_layout = QHBoxLayout()
        out_layout.addWidget(out_label)
        out_layout.addSpacing(10)
        out_layout.addWidget(out_col_input)
        out_layout.addSpacing(10)
        out_layout.addWidget(out_row_input)

        v_layout = QVBoxLayout(group)
        v_layout.addItem(cell1_layout)
        v_layout.addWidget(operator_label)
        v_layout.addItem(cell2_layout)
        v_layout.addWidget(equals_label)
        v_layout.addStretch(1)
        v_layout.addItem(out_layout)

        if add_dialog.exec():
            cell1 = cell1_col_input.currentText() + cell1_row_input.currentText()
            cell2 = cell2_col_input.currentText() + cell2_row_input.currentText()
            outCell = out_col_input.currentText() + out_row_input.currentText()
            return True

        return False

    @Slot()
    def action_sum(self) -> None:
        row_first = row_last = row_cur = 0
        col_first = col_last = col_cur = 0

        selected = self._table.selectedItems()

        if selected is not None:
            first = selected[0]
            last = selected[-1]
            row_first = self._table.row(first)
            row_last = self._table.row(last)
            col_first = self._table.column(first)
            col_last = self._table.column(last)

        current = self._table.currentItem()

        if current:
            row_cur = self._table.row(current)
            col_cur = self._table.column(current)

        cell1 = SpreadSheetItem.encode_pos(row_first, col_first)
        cell2 = SpreadSheetItem.encode_pos(row_last, col_last)
        out = SpreadSheetItem.encode_pos(row_cur, col_cur)

        if self.run_input_dialog(
            "Sum cells", "First cell:", "Last cell:",
            f"{(chr(0x03a3))}", "Output to:",
            cell1, cell2, out
        ):
            row, col = SpreadSheetItem.decode_pos(out)
            self._table.item(row, col).setText(f"sum {cell1} {cell2}")

    def action_math_helper(self, title: str, op: str) -> None:
        cell1 = "C1"
        cell2 = "C2"
        out = "C3"

        current = self._table.currentItem()
        if current:
            out = SpreadSheetItem.encode_pos(self._table.currentRow(), self._table.currentColumn())

        if self.run_input_dialog(title, "Cell 1", "Cell 2", op, "Output to:", cell1, cell2, out):
            row, col = SpreadSheetItem.decode_pos(out)
            self._table.item(row, col).setText(f"{op} {cell1} {cell2}")

    @Slot()
    def action_add(self) -> None:
        self.action_math_helper("Addition", "+")

    @Slot()
    def action_subtract(self) -> None:
        self.action_math_helper("Subtraction", "-")

    @Slot()
    def action_multiply(self) -> None:
        self.action_math_helper("Multiplication", "*")

    @Slot()
    def action_divide(self) -> None:
        self.action_math_helper("Division", "/")

    @Slot()
    def clear(self) -> None:
        selected_items = self._table.selectedItems()
        for item in selected_items:
            item.setText("")

    def setup_context_menu(self) -> None:
        self.addAction(self._cell_add_action)
        self.addAction(self._cell_sub_action)
        self.addAction(self._cell_mul_action)
        self.addAction(self._cell_div_action)
        self.addAction(self._cell_sum_action)
        self.addAction(self._first_separator)
        self.addAction(self._color_action)
        self.addAction(self._font_action)
        self.addAction(self._second_separator)
        self.addAction(self._clear_action)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

    def setup_contents(self) -> None:
        title_background = QBrush(Qt.GlobalColor.lightGray)
        title_font = self._table.font()
        title_font.setBold(True)

        # column 0
        self._table.setItem(0, 0, SpreadSheetItem("Item"))
        self._table.item(0, 0).setBackground(title_background)
        self._table.item(0, 0).setToolTip(
            "This column shows the purchased item/service"
        )
        self._table.item(0, 0).setFont(title_font)

        self._table.setItem(1, 0, SpreadSheetItem("AirportBus"))
        self._table.setItem(2, 0, SpreadSheetItem("Flight (Munich)"))
        self._table.setItem(3, 0, SpreadSheetItem("Lunch"))
        self._table.setItem(4, 0, SpreadSheetItem("Flight (LA)"))
        self._table.setItem(5, 0, SpreadSheetItem("Taxi"))
        self._table.setItem(6, 0, SpreadSheetItem("Dinner"))
        self._table.setItem(7, 0, SpreadSheetItem("Hotel"))
        self._table.setItem(8, 0, SpreadSheetItem("Flight (Oslo)"))
        self._table.setItem(9, 0, SpreadSheetItem("Total:"))

        self._table.item(9, 0).setFont(title_font)
        self._table.item(9, 0).setBackground(title_background)

        # column 1
        self._table.setItem(0, 1, SpreadSheetItem("Date"))
        self._table.item(0, 1).setBackground(title_background)
        self._table.item(0, 1).setToolTip(
            "This column shows the purchase date, double click to change"
        )
        self._table.item(0, 1).setFont(title_font)

        self._table.setItem(1, 1, SpreadSheetItem("15/6/2006"))
        self._table.setItem(2, 1, SpreadSheetItem("15/6/2006"))
        self._table.setItem(3, 1, SpreadSheetItem("15/6/2006"))
        self._table.setItem(4, 1, SpreadSheetItem("21/5/2006"))
        self._table.setItem(5, 1, SpreadSheetItem("16/6/2006"))
        self._table.setItem(6, 1, SpreadSheetItem("16/6/2006"))
        self._table.setItem(7, 1, SpreadSheetItem("16/6/2006"))
        self._table.setItem(8, 1, SpreadSheetItem("18/6/2006"))

        self._table.setItem(9, 1, SpreadSheetItem())
        self._table.item(9, 1).setBackground(title_background)

        # column 2
        self._table.setItem(0, 2, SpreadSheetItem("Price"))
        self._table.item(0, 2).setBackground(title_background)
        self._table.item(0, 2).setToolTip("This column shows the price of the purchase")
        self._table.item(0, 2).setFont(title_font)

        self._table.setItem(1, 2, SpreadSheetItem("150"))
        self._table.setItem(2, 2, SpreadSheetItem("2350"))
        self._table.setItem(3, 2, SpreadSheetItem("-14"))
        self._table.setItem(4, 2, SpreadSheetItem("980"))
        self._table.setItem(5, 2, SpreadSheetItem("5"))
        self._table.setItem(6, 2, SpreadSheetItem("120"))
        self._table.setItem(7, 2, SpreadSheetItem("300"))
        self._table.setItem(8, 2, SpreadSheetItem("1240"))

        self._table.setItem(9, 2, SpreadSheetItem())
        self._table.item(9, 2).setBackground(Qt.GlobalColor.lightGray)

        # column 3
        self._table.setItem(0, 3, SpreadSheetItem("Currency"))
        self._table.item(0, 3).setBackground(title_background)
        self._table.item(0, 3).setToolTip("This column shows the currency")
        self._table.item(0, 3).setFont(title_font)

        self._table.setItem(1, 3, SpreadSheetItem("NOK"))
        self._table.setItem(2, 3, SpreadSheetItem("NOK"))
        self._table.setItem(3, 3, SpreadSheetItem("EUR"))
        self._table.setItem(4, 3, SpreadSheetItem("EUR"))
        self._table.setItem(5, 3, SpreadSheetItem("USD"))
        self._table.setItem(6, 3, SpreadSheetItem("USD"))
        self._table.setItem(7, 3, SpreadSheetItem("USD"))
        self._table.setItem(8, 3, SpreadSheetItem("USD"))

        self._table.setItem(9, 3, SpreadSheetItem())
        self._table.item(9, 3).setBackground(Qt.GlobalColor.lightGray)

        # column 4
        self._table.setItem(0, 4, SpreadSheetItem("Ex. Rate"))
        self._table.item(0, 4).setBackground(title_background)
        self._table.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        self._table.item(0, 4).setFont(title_font)

        self._table.setItem(1, 4, SpreadSheetItem("1"))
        self._table.setItem(2, 4, SpreadSheetItem("1"))
        self._table.setItem(3, 4, SpreadSheetItem("8"))
        self._table.setItem(4, 4, SpreadSheetItem("8"))
        self._table.setItem(5, 4, SpreadSheetItem("7"))
        self._table.setItem(6, 4, SpreadSheetItem("7"))
        self._table.setItem(7, 4, SpreadSheetItem("7"))
        self._table.setItem(8, 4, SpreadSheetItem("7"))

        self._table.setItem(9, 4, SpreadSheetItem())
        self._table.item(9, 4).setBackground(title_background)

        # column 5
        self._table.setItem(0, 5, SpreadSheetItem("NOK"))
        self._table.item(0, 5).setBackground(title_background)
        self._table.item(0, 5).setToolTip("This column shows the expenses in NOK")
        self._table.item(0, 5).setFont(title_font)

        self._table.setItem(1, 5, SpreadSheetItem("* C2 E2"))
        self._table.setItem(2, 5, SpreadSheetItem("* C3 E3"))
        self._table.setItem(3, 5, SpreadSheetItem("* C4 E4"))
        self._table.setItem(4, 5, SpreadSheetItem("* C5 E5"))
        self._table.setItem(5, 5, SpreadSheetItem("* C6 E6"))
        self._table.setItem(6, 5, SpreadSheetItem("* C7 E7"))
        self._table.setItem(7, 5, SpreadSheetItem("* C8 E8"))
        self._table.setItem(8, 5, SpreadSheetItem("* C9 E9"))

        self._table.setItem(9, 5, SpreadSheetItem("sum F2 F9"))
        self._table.item(9, 5).setBackground(title_background)

    @Slot()
    def show_about(self) -> None:
        html_text = (
            "<HTML>"
            "<p><b>This demo shows use of <c>QTableWidget</c> with custom handling for"
            " individual cells.</b></p>"
            "<p>Using a customized table item we make it possible to have dynamic"
            " output in different cells. The content that is implemented for this"
            " particular demo is:"
            "<ul>"
            "<li>Adding two cells.</li>"
            "<li>Subtracting one cell from another.</li>"
            "<li>Multiplying two cells.</li>"
            "<li>Dividing one cell with another.</li>"
            "<li>Summing the contents of an arbitrary number of cells.</li>"
            "</HTML>")
        QMessageBox.about(self, "About Spreadsheet", html_text)
