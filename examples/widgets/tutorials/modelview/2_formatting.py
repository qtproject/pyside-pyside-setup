# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QBrush, QFont
from PySide6.QtWidgets import QApplication, QTableView

"""PySide6 port of the widgets/tutorials/modelview/2_formatting example from Qt v6.x"""


class MyModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def rowCount(self, parent=None):
        return 2

    def columnCount(self, parent=None):
        return 3

#! [1]
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        # generate a log message when this method gets called
        print(f"row {row}, col{col}, role {role}")

        if role == Qt.DisplayRole:
            if row == 0 and col == 1:
                return "<--left"
            if row == 1 and col == 1:
                return "right-->"
            return f"Row{row}, Column{col+1}"

        elif role == Qt.FontRole:
            if row == 0 and col == 0:  # change font only for cell(0,0)
                bold_font = QFont()
                bold_font.setBold(True)
                return bold_font

        elif role == Qt.BackgroundRole:
            if row == 1 and col == 2:  # change background only for cell(1,2)
                return QBrush(Qt.red)

        elif role == Qt.TextAlignmentRole:
            if row == 1 and col == 1:  # change text alignment only for cell(1,1)
                return Qt.AlignRight | Qt.AlignVCenter

        elif role == Qt.CheckStateRole:
            if row == 1 and col == 0:  # add a checkbox to cell(1,0)
                return Qt.Checked

        return None
#! [1]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table_view = QTableView()
    my_model = MyModel()
    table_view.setModel(my_model)
    table_view.show()
    sys.exit(app.exec())
