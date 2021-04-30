
#############################################################################
##
## Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
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

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QMainWindow, QFileDialog, QApplication)

from addresswidget import AddressWidget


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
        open_action = self.create_action("&Open...", file_menu, self.open_file)
        save_action = self.create_action("&Save As...", file_menu, self.save_file)
        file_menu.addSeparator()
        exit_action = self.create_action("E&xit", file_menu, self.close)

        # Populate the Tools menu
        add_action = self.create_action("&Add Entry...", tool_menu, self._address_widget.add_entry)
        self._edit_action = self.create_action("&Edit Entry...", tool_menu, self._address_widget.edit_entry)
        tool_menu.addSeparator()
        self._remove_action = self.create_action("&Remove Entry", tool_menu, self._address_widget.remove_entry)

        # Disable the edit and remove menu items initially, as there are
        # no items yet.
        self._edit_action.setEnabled(False)
        self._remove_action.setEnabled(False)

        # Wire up the updateActions slot
        self._address_widget.selection_changed.connect(self.update_actions)

    def create_action(self, text, menu, slot):
        """ Helper function to save typing when populating menus
            with action.
        """
        action = QAction(text, self)
        menu.addAction(action)
        action.triggered.connect(slot)
        return action

    # Quick  gotcha:
    #
    # QFiledialog.getOpenFilename and QFileDialog.get.SaveFileName don't
    # behave in PySide6 as they do in Qt, where they return a QString
    # containing the filename.
    #
    # In PySide6, these functions return a tuple: (filename, filter)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self)
        if filename:
            self._address_widget.read_from_file(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self)
        if filename:
            self._address_widget.write_to_file(filename)

    def update_actions(self, selection):
        """ Only allow the user to remove or edit an item if an item
            is actually selected.
        """
        indexes = selection.indexes()

        if len(indexes) > 0:
            self._remove_action.setEnabled(True)
            self._edit_action.setEnabled(True)
        else:
            self._remove_action.setEnabled(False)
            self._edit_action.setEnabled(False)


if __name__ == "__main__":
    """ Run the application. """
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
