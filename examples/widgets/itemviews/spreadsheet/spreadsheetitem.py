# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from typing import Any
from PySide6.QtCore import QMetaType, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class SpreadSheetItem(QTableWidgetItem):
    is_resolving = False

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    def data(self, role: int) -> Any:
        if role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.StatusTipRole:
            return self.formula()

        if role == Qt.ItemDataRole.DisplayRole:
            return self.display()

        t = str(self.display())

        if role == Qt.ItemDataRole.ForegroundRole:
            try:
                number = int(t)
                color = Qt.GlobalColor.red if number < 0 else Qt.GlobalColor.blue
            except ValueError:
                color = Qt.GlobalColor.black
            return color

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if t and (t[0].isdigit() or t[0] == '-'):
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return super().data(role)

    def setData(self, role: int, value: Any) -> None:
        super().setData(role, value)
        if self.tableWidget():
            self.tableWidget().viewport().update()

    def display(self) -> QMetaType.Type.QVariant:
        # avoid circular dependencies
        if self.is_resolving:
            return QMetaType.Type.QVariant

        self.is_resolving = True
        result = self.compute_formula(self.formula(), self.tableWidget(), self)
        self.is_resolving = False
        return result

    def formula(self) -> None:
        return str(super().data(Qt.ItemDataRole.DisplayRole))

    def compute_formula(self, formula: str, widget: QTableWidget, this) -> QMetaType.Type.QVariant:
        # check if the string is actually a formula or not
        list_ = formula.split(' ')
        if not list_ or not widget:
            return formula  # it is a normal string

        op = list_[0].lower() if list_[0] else ""

        first_row = -1
        first_col = -1
        second_row = -1
        second_col = -1

        if len(list_) > 1:
            SpreadSheetItem.decode_pos(list_[1])

        if len(list_) > 2:
            SpreadSheetItem.decode_pos(list_[2])

        start = widget.item(first_row, first_col)
        end = widget.item(second_row, second_col)

        first_val = int(start.text()) if start else 0
        second_val = int(end.text()) if start else 0

        if op == "sum":
            sum = 0
            for r in range(first_row, second_row + 1):
                for c in range(first_col, second_col + 1):
                    table_item = widget.item(r, c)
                    if table_item and table_item != this:
                        sum += int(table_item.text())

            result = sum
        elif op == "+":
            result = first_val + second_val
        elif op == "-":
            result = first_val - second_val
        elif op == "*":
            result = first_val * second_val
        elif op == "/":
            if second_val == 0:
                result = "nan"
            else:
                result = first_val / second_val
        elif op == "=":
            if start:
                result = start.text()
        else:
            result = formula

        return result

    def decode_pos(pos: str) -> tuple[int, int]:
        if (not pos):
            col = -1
            row = -1
        else:
            col = ord(pos[0].encode("latin1")) - ord('A')
            try:
                row = int(pos[1:]) - 1
            except ValueError:
                row = -1
        return row, col

    def encode_pos(row: int, col: int) -> str:
        return str(chr(col + ord('A'))) + str(row + 1)
