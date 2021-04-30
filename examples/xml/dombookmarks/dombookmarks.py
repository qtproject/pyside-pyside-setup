
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
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

"""PySide6 port of the xml/dombookmarks example from Qt v5.x"""

import sys

from PySide6.QtCore import QDir, QFile, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QApplication, QFileDialog, QHeaderView, QMainWindow, QMessageBox, QStyle, QTreeWidget, QTreeWidgetItem, QWidget)
from PySide6.QtXml import QDomDocument


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._xbel_tree = XbelTree()
        self.setCentralWidget(self._xbel_tree)

        self.create_actions()
        self.create_menus()

        self.statusBar().showMessage("Ready")

        self.setWindowTitle("DOM Bookmarks")
        self.resize(480, 320)

    def open(self):
        file_name = QFileDialog.getOpenFileName(self,
                "Open Bookmark File", QDir.currentPath(),
                "XBEL Files (*.xbel *.xml)")[0]

        if not file_name:
            return

        in_file = QFile(file_name)
        if not in_file.open(QFile.ReadOnly | QFile.Text):
            reason = in_file.errorString()
            QMessageBox.warning(self, "DOM Bookmarks",
                    f"Cannot read file {file_name}:\n{reason}.")
            return

        if self._xbel_tree.read(in_file):
            self.statusBar().showMessage("File loaded", 2000)

    def save_as(self):
        file_name = QFileDialog.getSaveFileName(self,
                "Save Bookmark File", QDir.currentPath(),
                "XBEL Files (*.xbel *.xml)")[0]

        if not file_name:
            return

        out_file = QFile(file_name)
        if not out_file.open(QFile.WriteOnly | QFile.Text):
            reason = out_file.errorString()
            QMessageBox.warning(self, "DOM Bookmarks",
                    "Cannot write file {fileName}:\n{reason}.")
            return

        if self._xbel_tree.write(out_file):
            self.statusBar().showMessage("File saved", 2000)

    def about(self):
        QMessageBox.about(self, "About DOM Bookmarks",
            "The <b>DOM Bookmarks</b> example demonstrates how to use Qt's "
            "DOM classes to read and write XML documents.")

    def create_actions(self):
        self._open_act = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self._save_as_act = QAction("&Save As...", self, shortcut="Ctrl+S",
                triggered=self.save_as)

        self._exit_act = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self._about_act = QAction("&About", self, triggered=self.about)

        self._about_qt_act = QAction("About &Qt", self,
                triggered=qApp.aboutQt)

    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._open_act)
        self._file_menu.addAction(self._save_as_act)
        self._file_menu.addAction(self._exit_act)

        self.menuBar().addSeparator()

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_qt_act)


class XbelTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setHeaderLabels(("Title", "Location"))

        self._dom_document = QDomDocument()

        self._dom_element_for_item = {}

        self._folder_icon = QIcon()
        self._bookmark_icon = QIcon()

        self._folder_icon.addPixmap(self.style().standardPixmap(QStyle.SP_DirClosedIcon),
                QIcon.Normal, QIcon.Off)
        self._folder_icon.addPixmap(self.style().standardPixmap(QStyle.SP_DirOpenIcon),
                QIcon.Normal, QIcon.On)
        self._bookmark_icon.addPixmap(self.style().standardPixmap(QStyle.SP_FileIcon))

    def read(self, device):
        ok, errorStr, errorLine, errorColumn = self._dom_document.setContent(device, True)
        if not ok:
            QMessageBox.information(self.window(), "DOM Bookmarks",
                    f"Parse error at line {errorLine}, column {errorColumn}:\n{errorStr}")
            return False

        root = self._dom_document.documentElement()
        if root.tagName() != 'xbel':
            QMessageBox.information(self.window(), "DOM Bookmarks",
                    "The file is not an XBEL file.")
            return False
        elif root.hasAttribute('version') and root.attribute('version') != '1.0':
            QMessageBox.information(self.window(), "DOM Bookmarks",
                    "The file is not an XBEL version 1.0 file.")
            return False

        self.clear()

        # It might not be connected.
        try:
            self.itemChanged.disconnect(self.update_dom_element)
        except:
            pass

        child = root.firstChildElement('folder')
        while not child.isNull():
            self.parse_folder_element(child)
            child = child.nextSiblingElement('folder')

        self.itemChanged.connect(self.update_dom_element)

        return True

    def write(self, device):
        INDENT_SIZE = 4

        out = QTextStream(device)
        self._dom_document.save(out, INDENT_SIZE)
        return True

    def update_dom_element(self, item, column):
        element = self._dom_element_for_item.get(id(item))
        if not element.isNull():
            if column == 0:
                old_title_element = element.firstChildElement('title')
                new_title_element = self._dom_document.createElement('title')

                new_title_text = self._dom_document.createTextNode(item.text(0))
                new_title_element.appendChild(new_title_text)

                element.replaceChild(new_title_element, old_title_element)
            else:
                if element.tagName() == 'bookmark':
                    element.setAttribute('href', item.text(1))

    def parse_folder_element(self, element, parentItem=None):
        item = self.create_item(element, parentItem)

        title = element.firstChildElement('title').text()
        if not title:
            title = "Folder"

        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setIcon(0, self._folder_icon)
        item.setText(0, title)

        folded = (element.attribute('folded') != 'no')
        item.setExpanded(not folded)

        child = element.firstChildElement()
        while not child.isNull():
            if child.tagName() == 'folder':
                self.parse_folder_element(child, item)
            elif child.tagName() == 'bookmark':
                child_item = self.create_item(child, item)

                title = child.firstChildElement('title').text()
                if not title:
                    title = "Folder"

                child_item.setFlags(item.flags() | Qt.ItemIsEditable)
                child_item.setIcon(0, self._bookmark_icon)
                child_item.setText(0, title)
                child_item.setText(1, child.attribute('href'))
            elif child.tagName() == 'separator':
                child_item = self.create_item(child, item)
                child_item.setFlags(item.flags() & ~(Qt.ItemIsSelectable | Qt.ItemIsEditable))
                child_item.setText(0, 30 * "\xb7")

            child = child.nextSiblingElement()

    def create_item(self, element, parentItem=None):
        item = QTreeWidgetItem()

        if parentItem is not None:
            item = QTreeWidgetItem(parentItem)
        else:
            item = QTreeWidgetItem(self)

        self._dom_element_for_item[id(item)] = element
        return item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    main_win.open()
    sys.exit(app.exec())
