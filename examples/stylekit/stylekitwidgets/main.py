# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtLabsStyleKit import QStyleKitStyle
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
                               QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                               QLineEdit, QMainWindow, QProgressBar, QPushButton,
                               QRadioButton, QScrollArea, QSizePolicy, QSlider, QSpinBox,
                               QVBoxLayout, QWidget)
from PySide6.QtCore import Qt, QSignalBlocker, Slot
from PySide6.QtGui import QIcon, QKeySequence

import rc_stylekitwidgets  # noqa: F401


PRESETS = [("Classic", ":/ClassicStyle.qml"),
           ("Flat", ":/FlatStyle.qml"),
           ("Neon", ":/NeonStyle.qml")]


class StyleControl(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)

        style = QApplication.style()
        self.m_style = style if isinstance(style, QStyleKitStyle) else None

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        settings_layout = QFormLayout(self)

        self.m_theme_combo = QComboBox()
        self.m_style_path_combo = QComboBox()

        for preset in PRESETS:
            self.m_style_path_combo.addItem(preset[0], preset[1])
        self.m_style_path_combo.setCurrentIndex(0)

        settings_layout.addRow("Style", self.m_style_path_combo)
        settings_layout.addRow("Theme", self.m_theme_combo)

        if self.m_style is not None:
            self._refresh_themes()
        else:
            self.setEnabled(False)

        self.m_style_path_combo.activated.connect(self._style_path_combo_activated)
        self.m_theme_combo.activated.connect(self._theme_combo_activated)

    def _refresh_themes(self):
        names = self.m_style.themeNames()
        current = self.m_style.themeName()
        with QSignalBlocker(self.m_theme_combo):
            self.m_theme_combo.clear()
            self.m_theme_combo.addItems(names)
            idx = self.m_theme_combo.findText(current)
            if idx >= 0:
                self.m_theme_combo.setCurrentIndex(idx)

    def _set_style_path(self, path: str):
        self.m_style.setStylePath(path)
        self._refresh_themes()

    @Slot(int)
    def _style_path_combo_activated(self, index: int):
        data = self.m_style_path_combo.itemData(index)
        self._set_style_path(data or self.m_style_path_combo.itemText(index))

    @Slot(int)
    def _theme_combo_activated(self, _index: int):
        self.m_style.setThemeName(self.m_theme_combo.currentText())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit), "Quit",
                            QKeySequence(QKeySequence.StandardKey.Quit), self.close)
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout), "About Qt",
                            QKeySequence(QKeySequence.StandardKey.HelpContents),
                            QApplication.aboutQt)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        content_layout = QVBoxLayout(scroll_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Buttons
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QHBoxLayout(buttons_group)
        normal_button = QPushButton("Normal")
        checkable_button = QPushButton("Checkable")
        checkable_button.setCheckable(True)
        disabled_button = QPushButton("Disabled")
        disabled_button.setEnabled(False)
        flat_button = QPushButton("Flat")
        flat_button.setFlat(True)
        buttons_layout.addWidget(normal_button)
        buttons_layout.addWidget(checkable_button)
        buttons_layout.addWidget(disabled_button)
        buttons_layout.addWidget(flat_button)
        buttons_layout.addStretch()
        content_layout.addWidget(buttons_group)

        # CheckBoxes and RadioButtons
        check_radio_group = QGroupBox("CheckBoxes and RadioButtons")
        check_radio_layout = QGridLayout(check_radio_group)
        check_radio_layout.setColumnStretch(3, 1)

        check_box1 = QCheckBox("Mango")
        check_box1.setChecked(True)
        check_box2 = QCheckBox("Avocado")
        check_box3 = QCheckBox("Banano")
        check_box3.setChecked(True)

        radio_button1 = QRadioButton("Pasta")
        radio_button2 = QRadioButton("Lasagna")
        radio_button2.setChecked(True)
        radio_button3 = QRadioButton("Burrita")

        radio_group = QButtonGroup(scroll_widget)
        radio_group.addButton(radio_button1)
        radio_group.addButton(radio_button2)
        radio_group.addButton(radio_button3)

        check_radio_layout.addWidget(check_box1, 0, 0)
        check_radio_layout.addWidget(check_box2, 0, 1)
        check_radio_layout.addWidget(check_box3, 0, 2)
        check_radio_layout.addWidget(radio_button1, 1, 0)
        check_radio_layout.addWidget(radio_button2, 1, 1)
        check_radio_layout.addWidget(radio_button3, 1, 2)
        content_layout.addWidget(check_radio_group)

        # Text Inputs
        text_inputs_group = QGroupBox("Text Inputs")
        text_inputs_layout = QHBoxLayout(text_inputs_group)
        line_edit1 = QLineEdit()
        line_edit1.setPlaceholderText("Potato")
        line_edit2 = QLineEdit()
        line_edit2.setPlaceholderText("Tomato")
        text_inputs_layout.addWidget(line_edit1)
        text_inputs_layout.addWidget(line_edit2)
        content_layout.addWidget(text_inputs_group)

        # Misc
        misc_group = QGroupBox("Misc")
        misc_layout = QHBoxLayout(misc_group)
        spin_box = QSpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(42)
        combo_box = QComboBox()
        combo_box.addItems(["One", "February", "Aramis", "Winter", "Friday"])
        misc_layout.addWidget(spin_box)
        misc_layout.addWidget(combo_box)
        misc_layout.addStretch()
        content_layout.addWidget(misc_group)

        # Sliders
        sliders_group = QGroupBox("Sliders")
        sliders_group.setMinimumHeight(250)
        sliders_layout = QHBoxLayout(sliders_group)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        vertical_slider = QSlider(Qt.Orientation.Vertical)
        vertical_slider.setRange(0, 100)
        vertical_slider.setValue(30)
        sliders_layout.addWidget(slider)
        sliders_layout.addWidget(vertical_slider)
        sliders_layout.addStretch()
        content_layout.addWidget(sliders_group)

        # Progress Bar
        progress_group = QGroupBox("Progress Bar")
        progress_layout = QHBoxLayout(progress_group)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(20)
        progress_layout.addWidget(progress_bar)
        content_layout.addWidget(progress_group)

        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.addWidget(scroll_area)
        central_layout.addWidget(StyleControl(central_widget))
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    style = QStyleKitStyle(PRESETS[0][1])
    if not any(arg == "-style" for arg in sys.argv[1:]):
        QApplication.setStyle(style)

    window = MainWindow()
    window.setWindowTitle("StyleKit Widgets Example")
    window.resize(800, 600)

    window.show()

    sys.exit(app.exec())
