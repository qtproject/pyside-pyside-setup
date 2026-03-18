# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QMainWindow, QFileDialog, QApplication

from addresswidget import AddressWidget


FILTER = "Data files (*.dat)"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._address_widget = AddressWidget()
        self.setCentralWidget(self._address_widget)
        self.create_menus()
        self.setWindowTitle("Address Book")

    def create_menus(self):
        # Create the main menuBar menu items
        file_menu = self.menuBar().addMenu("&File")
        tool_menu = self.menuBar().addMenu("&Tools")

        # Populate the File menu
        self.open_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), "&Open...", self)
        self.open_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Open))
        self.open_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_action)

        self.save_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), "&Save As...",
                                   self)
        self.save_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Save))
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        self.exit_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit), "E&xit", self)
        self.exit_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Quit))
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

        # Populate the Tools menu
        self.add_action = tool_menu.addAction("&Add Entry...", self._address_widget.add_entry)
        self.add_action.setShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier
                                                 | Qt.Key.Key_A))
        self._edit_action = tool_menu.addAction("&Edit Entry...", self._address_widget.edit_entry)
        tool_menu.addSeparator()
        self._remove_action = tool_menu.addAction("&Remove Entry",
                                                  self._address_widget.remove_entry)

        # Disable the edit and remove menu items initially, as there are
        # no items yet.
        self._edit_action.setEnabled(False)
        self._remove_action.setEnabled(False)

        # Wire up the updateActions slot
        self._address_widget.selection_changed.connect(self.update_actions)

    # Quick  gotcha:
    #
    # QFiledialog.getOpenFilename and QFileDialog.get.SaveFileName don't
    # behave in PySide6 as they do in Qt, where they return a QString
    # containing the filename.
    #
    # In PySide6, these functions return a tuple: (filename, filter)

    @Slot()
    def open_file(self):
        dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", dir, FILTER)
        if filename:
            self._address_widget.read_from_file(filename)
            self.statusBar().showMessage(f"Read {filename}")

    @Slot()
    def save_file(self):
        dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filename, _ = QFileDialog.getSaveFileName(self, "Save File As", dir, FILTER)
        if filename:
            self._address_widget.write_to_file(filename)
            self.statusBar().showMessage(f"Wrote {filename}")

    def update_actions(self, selection):
        """ Only allow the user to remove or edit an item if an item
            is actually selected.
        """
        enabled = bool(selection.indexes())
        self._remove_action.setEnabled(enabled)
        self._edit_action.setEnabled(enabled)


if __name__ == "__main__":
    """ Run the application. """
    app = QApplication(sys.argv)
    mw = MainWindow()
    availableGeometry = mw.screen().availableGeometry()
    mw.resize(availableGeometry.width() / 3, availableGeometry.height() / 3)
    mw.show()
    sys.exit(app.exec())
