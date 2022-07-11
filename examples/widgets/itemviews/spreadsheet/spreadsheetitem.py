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

from typing import Any, Tuple
from PySide6.QtCore import QMetaType, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class SpreadSheetItem(QTableWidgetItem):
    is_resolving = False

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    def data(self, role: int) -> Any:
        if role == Qt.EditRole or role == Qt.StatusTipRole:
            return self.formula()

        if role == Qt.DisplayRole:
            return self.display()

        t = str(self.display())

        if role == Qt.ForegroundRole:
            try:
                number = int(t)
                color = Qt.red if number < 0 else Qt.blue
            except ValueError:
                color = Qt.black
            return color

        if role == Qt.TextAlignmentRole:
            if t and (t[0].isdigit() or t[0] == '-'):
                return int(Qt.AlignRight | Qt.AlignVCenter)

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
        return str(super().data(Qt.DisplayRole))

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

    def decode_pos(pos: str) -> Tuple[int, int]:
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
