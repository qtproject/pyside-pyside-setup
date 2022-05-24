# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the widgets/dialogs/extension example from Qt v5.x"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog,
                               QDialogButtonBox, QGridLayout, QHBoxLayout,
                               QLabel, QLayout, QLineEdit, QPushButton,
                               QVBoxLayout, QWidget)


class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        label = QLabel("Find &what:")
        line_edit = QLineEdit()
        label.setBuddy(line_edit)

        case_check_box = QCheckBox("Match &case")
        from_start_check_box = QCheckBox("Search from &start")
        from_start_check_box.setChecked(True)

        find_button = QPushButton("&Find")
        find_button.setDefault(True)

        more_button = QPushButton("&More")
        more_button.setCheckable(True)
        more_button.setAutoDefault(False)

        button_box = QDialogButtonBox(Qt.Vertical)
        button_box.addButton(find_button, QDialogButtonBox.ActionRole)
        button_box.addButton(more_button, QDialogButtonBox.ActionRole)

        extension = QWidget()

        whole_words_check_box = QCheckBox("&Whole words")
        backward_check_box = QCheckBox("Search &backward")
        search_selection_check_box = QCheckBox("Search se&lection")

        more_button.toggled.connect(extension.setVisible)

        extension_layout = QVBoxLayout()
        extension_layout.setContentsMargins(0, 0, 0, 0)
        extension_layout.addWidget(whole_words_check_box)
        extension_layout.addWidget(backward_check_box)
        extension_layout.addWidget(search_selection_check_box)
        extension.setLayout(extension_layout)

        top_left_layout = QHBoxLayout()
        top_left_layout.addWidget(label)
        top_left_layout.addWidget(line_edit)

        left_layout = QVBoxLayout()
        left_layout.addLayout(top_left_layout)
        left_layout.addWidget(case_check_box)
        left_layout.addWidget(from_start_check_box)
        left_layout.addStretch(1)

        main_layout = QGridLayout(self)
        main_layout.setSizeConstraint(QLayout.SetFixedSize)
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addWidget(button_box, 0, 1)
        main_layout.addWidget(extension, 1, 0, 1, 2)

        self.setWindowTitle("Extension")
        extension.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = FindDialog()
    sys.exit(dialog.exec())
