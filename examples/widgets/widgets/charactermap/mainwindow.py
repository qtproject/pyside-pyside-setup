# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt, QSignalBlocker, Slot
from PySide6.QtGui import QGuiApplication, QClipboard, QFont, QFontDatabase
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFontComboBox,
                               QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from characterwidget import CharacterWidget
from fontinfodialog import FontInfoDialog


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._character_widget = CharacterWidget()
        self._filter_combo = QComboBox()
        self._style_combo = QComboBox()
        self._size_combo = QComboBox()
        self._font_combo = QFontComboBox()
        self._line_edit = QLineEdit()
        self._scroll_area = QScrollArea()
        self._font_merging = QCheckBox()

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Quit", self.close)
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("Show Font Info", self.show_info)
        help_menu.addAction("About &Qt", qApp.aboutQt)

        central_widget = QWidget()

        self._filter_label = QLabel("Filter:")
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("All", int(QFontComboBox.AllFonts.value))
        self._filter_combo.addItem("Scalable", int(QFontComboBox.ScalableFonts.value))
        self._filter_combo.addItem("Monospaced", int(QFontComboBox.MonospacedFonts.value))
        self._filter_combo.addItem("Proportional", int(QFontComboBox.ProportionalFonts.value))
        self._filter_combo.setCurrentIndex(0)
        self._filter_combo.currentIndexChanged.connect(self.filter_changed)

        self._font_label = QLabel("Font:")
        self._font_combo = QFontComboBox()
        self._size_label = QLabel("Size:")
        self._size_combo = QComboBox()
        self._style_label = QLabel("Style:")
        self._style_combo = QComboBox()
        self._font_merging_label = QLabel("Automatic Font Merging:")
        self._font_merging = QCheckBox()
        self._font_merging.setChecked(True)

        self._scroll_area = QScrollArea()
        self._character_widget = CharacterWidget()
        self._scroll_area.setWidget(self._character_widget)
        self.find_styles(self._font_combo.currentFont())
        self.find_sizes(self._font_combo.currentFont())

        self._line_edit = QLineEdit()
        self._line_edit.setClearButtonEnabled(True)
        self._clipboard_button = QPushButton("To clipboard")
        self._font_combo.currentFontChanged.connect(self.find_styles)
        self._font_combo.currentFontChanged.connect(self.find_sizes)
        self._font_combo.currentFontChanged.connect(self._character_widget.update_font)
        self._size_combo.currentTextChanged.connect(self._character_widget.update_size)
        self._style_combo.currentTextChanged.connect(self._character_widget.update_style)
        self._character_widget.character_selected.connect(self.insert_character)

        self._clipboard_button.clicked.connect(self.update_clipboard)
        self._font_merging.toggled.connect(self._character_widget.update_font_merging)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self._filter_label)
        controls_layout.addWidget(self._filter_combo, 1)
        controls_layout.addWidget(self._font_label)
        controls_layout.addWidget(self._font_combo, 1)
        controls_layout.addWidget(self._size_label)
        controls_layout.addWidget(self._size_combo, 1)
        controls_layout.addWidget(self._style_label)
        controls_layout.addWidget(self._style_combo, 1)
        controls_layout.addWidget(self._font_merging_label)
        controls_layout.addWidget(self._font_merging, 1)
        controls_layout.addStretch(1)

        line_layout = QHBoxLayout()
        line_layout.addWidget(self._line_edit, 1)
        line_layout.addSpacing(12)
        line_layout.addWidget(self._clipboard_button)

        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(controls_layout)
        central_layout.addWidget(self._scroll_area, 1)
        central_layout.addSpacing(4)
        central_layout.addLayout(line_layout)

        self.setCentralWidget(central_widget)
        self.setWindowTitle("Character Map")

    @Slot(QFont)
    def find_styles(self, font):
        current_item = self._style_combo.currentText()
        self._style_combo.clear()
        styles = QFontDatabase.styles(font.family())
        for style in styles:
            self._style_combo.addItem(style)

        style_index = self._style_combo.findText(current_item)

        if style_index == -1:
            self._style_combo.setCurrentIndex(0)
        else:
            self._style_combo.setCurrentIndex(style_index)

    @Slot(int)
    def filter_changed(self, f):
        filter = QFontComboBox.FontFilter(self._filter_combo.itemData(f))
        self._font_combo.setFontFilters(filter)
        count = self._font_combo.count()
        self.statusBar().showMessage(f"{count} font(s) found")

    @Slot(QFont)
    def find_sizes(self, font):
        current_size = self._size_combo.currentText()
        with QSignalBlocker(self._size_combo):
            # sizeCombo signals are now blocked until end of scope
            self._size_combo.clear()

            style = QFontDatabase.styleString(font)
            if QFontDatabase.isSmoothlyScalable(font.family(), style):
                sizes = QFontDatabase.standardSizes()
                for size in sizes:
                    self._size_combo.addItem(f"{size}")
                    self._size_combo.setEditable(True)
            else:
                sizes = QFontDatabase.smoothSizes(font.family(), style)
                for size in sizes:
                    self._size_combo.addItem(f"{size}")
                    self._size_combo.setEditable(False)

        size_index = self._size_combo.findText(current_size)

        if size_index == -1:
            self._size_combo.setCurrentIndex(max(0, self._size_combo.count() / 3))
        else:
            self._size_combo.setCurrentIndex(size_index)

    @Slot(str)
    def insert_character(self, character):
        self._line_edit.insert(character)

    @Slot()
    def update_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._line_edit.text(), QClipboard.Clipboard)
        clipboard.setText(self._line_edit.text(), QClipboard.Selection)

    @Slot()
    def show_info(self):
        screen_geometry = self.screen().geometry()
        dialog = FontInfoDialog(self)
        dialog.setWindowTitle("Fonts")
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.resize(screen_geometry.width() / 4, screen_geometry.height() / 4)
        dialog.show()
