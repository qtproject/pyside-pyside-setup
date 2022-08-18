# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


from PySide6.QtCore import QDir, QFile, QIODevice, QUrl, Qt, Slot
from PySide6.QtGui import QFontDatabase
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox

from ui_mainwindow import Ui_MainWindow
from document import Document
from previewpage import PreviewPage


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_file_path = ''
        self.m_content = Document()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self._ui.editor.setFont(font)
        self._ui.preview.setContextMenuPolicy(Qt.NoContextMenu)
        self._page = PreviewPage(self)
        self._ui.preview.setPage(self._page)

        self._ui.editor.textChanged.connect(self.plainTextEditChanged)

        self._channel = QWebChannel(self)
        self._channel.registerObject("content", self.m_content)
        self._page.setWebChannel(self._channel)

        self._ui.preview.setUrl(QUrl("qrc:/index.html"))

        self._ui.actionNew.triggered.connect(self.onFileNew)
        self._ui.actionOpen.triggered.connect(self.onFileOpen)
        self._ui.actionSave.triggered.connect(self.onFileSave)
        self._ui.actionSaveAs.triggered.connect(self.onFileSaveAs)
        self._ui.actionExit.triggered.connect(self.close)

        self._ui.editor.document().modificationChanged.connect(self._ui.actionSave.setEnabled)

        defaultTextFile = QFile(":/default.md")
        defaultTextFile.open(QIODevice.ReadOnly)
        data = defaultTextFile.readAll()
        self._ui.editor.setPlainText(data.data().decode('utf8'))

    @Slot()
    def plainTextEditChanged(self):
        self.m_content.setText(self._ui.editor.toPlainText())

    @Slot(str)
    def openFile(self, path):
        f = QFile(path)
        name = QDir.toNativeSeparators(path)
        if not f.open(QIODevice.ReadOnly):
            error = f.errorString()
            QMessageBox.warning(self, self.windowTitle(),
                                f"Could not open file {name}: {error}")
            return
        self.m_file_path = path
        data = f.readAll()
        self._ui.editor.setPlainText(data.data().decode('utf8'))
        self.statusBar().showMessage(f"Opened {name}")

    def isModified(self):
        return self._ui.editor.document().isModified()

    @Slot()
    def onFileNew(self):
        if self.isModified():
            m = "You have unsaved changes. Do you want to create a new document anyway?"
            button = QMessageBox.question(self, self.windowTitle(), m)
            if button != QMessageBox.Yes:
                return

        self.m_file_path = ''
        self._ui.editor.setPlainText(tr("## New document"))
        self._ui.editor.document().setModified(False)

    @Slot()
    def onFileOpen(self):
        if self.isModified():
            m = "You have unsaved changes. Do you want to open a new document anyway?"
            button = QMessageBox.question(self, self.windowTitle(), m)
            if button != QMessageBox.Yes:
                return
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Open MarkDown File")
        dialog.setMimeTypeFilters(["text/markdown"])
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if dialog.exec() == QDialog.Accepted:
            self.openFile(dialog.selectedFiles()[0])

    @Slot()
    def onFileSave(self):
        if not self.m_file_path:
            self.onFileSaveAs()
        if not self.m_file_path:
            return

        f = QFile(self.m_file_path)
        name = QDir.toNativeSeparators(self.m_file_path)
        if not f.open(QIODevice.WriteOnly | QIODevice.Text):
            error = f.errorString()
            QMessageBox.warning(self, windowTitle(),
                                f"Could not write to file {name}: {error}")
            return
        text = self._ui.editor.toPlainText()
        f.write(bytes(text, encoding='utf8'))
        f.close()
        self.statusBar().showMessage(f"Wrote {name}")

    @Slot()
    def onFileSaveAs(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Open MarkDown File")
        dialog.setMimeTypeFilters(["text/markdown"])
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("md")
        if dialog.exec() != QDialog.Accepted:
            return
        path = dialog.selectedFiles()[0]
        self.m_file_path = path
        self.onFileSave()

    def closeEvent(self, event):
        if self.isModified():
            m = "You have unsaved changes. Do you want to exit anyway?"
            button = QMessageBox.question(self, self.windowTitle(), m)
            if button != QMessageBox.Yes:
                event.ignore()
            else:
                event.accept()
