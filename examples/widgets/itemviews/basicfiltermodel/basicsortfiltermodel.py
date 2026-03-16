# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from enum import Enum
from PySide6.QtCore import (QDate, QDateTime, QRangeModel, QRegularExpression,
                            QSortFilterProxyModel, QTime, Qt, Slot)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QTreeView, QVBoxLayout, QWidget)


class Syntax(Enum):
    REGULAR_EXPRESSION = 0
    WILDCARD = 1
    FIXED_STRING = 2


HEADERS = ["Subject", "Sender", "Date"]


MAILS = [
    ["RE: Sports", "Petra Schmidt <petras@nospam.com>",
     QDateTime(QDate(2007, 1, 5), QTime(12, 1))],
    ["AW: Sports", "Rolf Newschweinstein <rolfn@nospam.com>",
     QDateTime(QDate(2007, 1, 5), QTime(12, 0))],
    ["Sports", "Linda Smith <linda.smith@nospam.com>",
     QDateTime(QDate(2007, 1, 5), QTime(11, 33))],
    ["Re: Accounts", "Andy <andy@nospam.com>",
     QDateTime(QDate(2007, 1, 3), QTime(14, 26))],
    ["Re: Accounts", "Joe Bloggs <joe@bloggs.com>",
     QDateTime(QDate(2007, 1, 3), QTime(14, 18))],
    ["Re: Expenses", "Andy <andy@nospam.com>",
     QDateTime(QDate(2007, 1, 2), QTime(16, 5))],
    ["Expenses", "Joe Bloggs <joe@bloggs.com>",
     QDateTime(QDate(2006, 12, 25), QTime(11, 39))],
    ["Accounts", "pascale@nospam.com",
     QDateTime(QDate(2006, 12, 31), QTime(12, 50))],
    ["Radically new concept", "Grace K. <grace@software-inc.com>",
     QDateTime(QDate(2006, 12, 22), QTime(9, 44))],
    ["Happy New Year!", "Grace K. <grace@software-inc.com>",
     QDateTime(QDate(2006, 12, 31), QTime(17, 3))]
]


class MailModel(QRangeModel):
    def __init__(self, parent=None):
        super().__init__(MAILS, parent)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return HEADERS[section]
        return None


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.setDynamicSortFilter(True)

        self._source_group_box = QGroupBox("Original Model")
        self._proxy_group_box = QGroupBox("Sorted/Filtered Model")

        self._source_view = QTreeView()
        self._source_view.setRootIsDecorated(False)
        self._source_view.setAlternatingRowColors(True)

        self._proxy_view = QTreeView()
        self._proxy_view.setRootIsDecorated(False)
        self._proxy_view.setAlternatingRowColors(True)
        self._proxy_view.setModel(self._proxy_model)
        self._proxy_view.setSortingEnabled(True)

        self._sort_case_sensitivity_check_box = QCheckBox("Case sensitive sorting")
        self._filter_case_sensitivity_check_box = QCheckBox("Case sensitive filter")

        self._filter_pattern_line_edit = QLineEdit()
        self._filter_pattern_line_edit.setClearButtonEnabled(True)

        self._filter_syntax_combo_box = QComboBox()
        self._filter_syntax_combo_box.addItem("Regular expression",
                                              Syntax.REGULAR_EXPRESSION)
        self._filter_syntax_combo_box.addItem("Wildcard",
                                              Syntax.WILDCARD)
        self._filter_syntax_combo_box.addItem("Fixed string",
                                              Syntax.FIXED_STRING)

        self._filter_column_combo_box = QComboBox()
        for header in HEADERS:
            self._filter_column_combo_box.addItem(header)
        self._filter_column_label = QLabel("Filter &column:")

        self._filter_pattern_line_edit.textChanged.connect(self.filter_reg_exp_changed)
        self._filter_syntax_combo_box.currentIndexChanged.connect(self.filter_reg_exp_changed)
        self._filter_column_combo_box.currentIndexChanged.connect(self.filter_column_changed)
        self._filter_case_sensitivity_check_box.toggled.connect(self.filter_reg_exp_changed)
        self._sort_case_sensitivity_check_box.toggled.connect(self.sort_changed)

        source_layout = QHBoxLayout(self._source_group_box)
        source_layout.addWidget(self._source_view)

        proxy_layout = QVBoxLayout(self._proxy_group_box)
        proxy_layout.addWidget(self._proxy_view)

        form_layout = QFormLayout()
        form_layout.addRow("&Filter pattern:", self._filter_pattern_line_edit)
        form_layout.addRow("Filter &syntax:", self._filter_syntax_combo_box)
        form_layout.addRow("Filter &column:", self._filter_column_combo_box)
        proxy_layout.addLayout(form_layout)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self._filter_case_sensitivity_check_box)
        checkbox_layout.addWidget(self._sort_case_sensitivity_check_box)
        proxy_layout.addLayout(checkbox_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._source_group_box)
        main_layout.addWidget(self._proxy_group_box)

        self.setWindowTitle("Basic Sort/Filter Model")
        screen_geometry = self.screen().geometry()
        self.resize(screen_geometry.width() / 2, screen_geometry.height() * 2 / 3)

        self._proxy_view.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self._filter_column_combo_box.setCurrentIndex(1)

        self._filter_pattern_line_edit.setText("Andy|Grace")
        self._filter_case_sensitivity_check_box.setChecked(True)
        self._sort_case_sensitivity_check_box.setChecked(True)

    def set_source_model(self, model):
        self._proxy_model.setSourceModel(model)
        self._source_view.setModel(model)

    @Slot()
    def filter_reg_exp_changed(self):
        pattern = self._filter_pattern_line_edit.text()
        match self._filter_syntax_combo_box.currentData():
            case Syntax.WILDCARD:
                pattern = QRegularExpression.wildcardToRegularExpression(pattern)
            case Syntax.FIXED_STRING:
                pattern = QRegularExpression.escape(pattern)

        reg_exp = QRegularExpression(pattern)
        if not self._filter_case_sensitivity_check_box.isChecked():
            options = reg_exp.patternOptions()
            options |= QRegularExpression.PatternOption.CaseInsensitiveOption
            reg_exp.setPatternOptions(options)
        self._proxy_model.setFilterRegularExpression(reg_exp)

    @Slot()
    def filter_column_changed(self):
        self._proxy_model.setFilterKeyColumn(self._filter_column_combo_box.currentIndex())

    @Slot()
    def sort_changed(self):
        if self._sort_case_sensitivity_check_box.isChecked():
            case_sensitivity = Qt.CaseSensitivity.CaseSensitive
        else:
            case_sensitivity = Qt.CaseSensitivity.CaseInsensitive

        self._proxy_model.setSortCaseSensitivity(case_sensitivity)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.set_source_model(MailModel(window))
    window.show()
    sys.exit(app.exec())
