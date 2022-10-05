# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the widgets/layouts/dynamiclayouts example from Qt v5.x"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QApplication, QDialog, QLayout, QGridLayout,
                               QMessageBox, QGroupBox, QSpinBox, QSlider,
                               QProgressBar, QDial, QDialogButtonBox,
                               QComboBox, QLabel)


class Dialog(QDialog):
    def __init__(self):
        super().__init__()

        self._rotable_widgets = []

        self.create_rotable_group_box()
        self.create_options_group_box()
        self.create_button_box()

        main_layout = QGridLayout()
        main_layout.addWidget(self._rotable_group_box, 0, 0)
        main_layout.addWidget(self._options_group_box, 1, 0)
        main_layout.addWidget(self._button_box, 2, 0)
        main_layout.setSizeConstraint(QLayout.SetMinimumSize)

        self._main_layout = main_layout
        self.setLayout(self._main_layout)

        self.setWindowTitle("Dynamic Layouts")

    def rotate_widgets(self):
        count = len(self._rotable_widgets)
        if count % 2 == 1:
            raise AssertionError("Number of widgets must be even")

        for widget in self._rotable_widgets:
            self._rotable_layout.removeWidget(widget)

        self._rotable_widgets.append(self._rotable_widgets.pop(0))

        for i in range(count // 2):
            self._rotable_layout.addWidget(self._rotable_widgets[count - i - 1], 0, i)
            self._rotable_layout.addWidget(self._rotable_widgets[i], 1, i)

    def buttons_orientation_changed(self, index):
        self._main_layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.setMinimumSize(0, 0)

        orientation = Qt.Orientation(self._buttons_orientation_combo_box.itemData(index))

        if orientation == self._button_box.orientation():
            return

        self._main_layout.removeWidget(self._button_box)

        spacing = self._main_layout.spacing()

        old_size_hint = self._button_box.sizeHint() + QSize(spacing, spacing)
        self._button_box.setOrientation(orientation)
        new_size_hint = self._button_box.sizeHint() + QSize(spacing, spacing)

        if orientation == Qt.Horizontal:
            self._main_layout.addWidget(self._button_box, 2, 0)
            self.resize(self.size() + QSize(-old_size_hint.width(), new_size_hint.height()))
        else:
            self._main_layout.addWidget(self._button_box, 0, 3, 2, 1)
            self.resize(self.size() + QSize(new_size_hint.width(), -old_size_hint.height()))

        self._main_layout.setSizeConstraint(QLayout.SetDefaultConstraint)

    def show_help(self):
        QMessageBox.information(self, "Dynamic Layouts Help",
                            "This example shows how to change layouts "
                            "dynamically.")

    def create_rotable_group_box(self):
        self._rotable_group_box = QGroupBox("Rotable Widgets")

        self._rotable_widgets.append(QSpinBox())
        self._rotable_widgets.append(QSlider())
        self._rotable_widgets.append(QDial())
        self._rotable_widgets.append(QProgressBar())
        count = len(self._rotable_widgets)
        for i in range(count):
            element = self._rotable_widgets[(i + 1) % count]
            self._rotable_widgets[i].valueChanged[int].connect(element.setValue)

        self._rotable_layout = QGridLayout()
        self._rotable_group_box.setLayout(self._rotable_layout)

        self.rotate_widgets()

    def create_options_group_box(self):
        self._options_group_box = QGroupBox("Options")

        buttons_orientation_label = QLabel("Orientation of buttons:")

        buttons_orientation_combo_box = QComboBox()
        buttons_orientation_combo_box.addItem("Horizontal", Qt.Horizontal)
        buttons_orientation_combo_box.addItem("Vertical", Qt.Vertical)
        buttons_orientation_combo_box.currentIndexChanged[int].connect(self.buttons_orientation_changed)

        self._buttons_orientation_combo_box = buttons_orientation_combo_box

        options_layout = QGridLayout()
        options_layout.addWidget(buttons_orientation_label, 0, 0)
        options_layout.addWidget(self._buttons_orientation_combo_box, 0, 1)
        options_layout.setColumnStretch(2, 1)
        self._options_group_box.setLayout(options_layout)

    def create_button_box(self):
        self._button_box = QDialogButtonBox()

        close_button = self._button_box.addButton(QDialogButtonBox.Close)
        help_button = self._button_box.addButton(QDialogButtonBox.Help)
        rotate_widgets_button = self._button_box.addButton("Rotate &Widgets", QDialogButtonBox.ActionRole)

        rotate_widgets_button.clicked.connect(self.rotate_widgets)
        close_button.clicked.connect(self.close)
        help_button.clicked.connect(self.show_help)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.exec()
