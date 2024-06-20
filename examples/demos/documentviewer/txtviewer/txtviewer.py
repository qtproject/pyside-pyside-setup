# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import (QDialog, QFileDialog,
                               QPlainTextEdit)
from PySide6.QtGui import QAction, QGuiApplication, QIcon, QKeySequence
from PySide6.QtCore import QDir, QFile, QTextStream, Qt, Slot

from abstractviewer import AbstractViewer


class TxtViewer(AbstractViewer):
    def __init__(self):
        super().__init__()
        self.uiInitialized.connect(self.setupTxtUi)

    def init(self, file, parent, mainWindow):
        self._textEdit = QPlainTextEdit(parent)
        super().init(file, self._textEdit, mainWindow)

    def viewerName(self):
        return "TxtViewer"

    def supportedMimeTypes(self):
        return ["text/plain"]

    @Slot()
    def setupTxtUi(self):
        editMenu = self.addMenu("Edit")
        editToolBar = self.addToolBar("Edit")
        cutIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditCut,
                                  QIcon(":/demos/documentviewer/images/cut.png"))
        cutAct = QAction(cutIcon, "Cut", self)
        cutAct.setShortcuts(QKeySequence.Cut)
        cutAct.setStatusTip("Cut the current selection's contents to the clipboard")
        cutAct.triggered.connect(self._textEdit.cut)
        editMenu.addAction(cutAct)
        editToolBar.addAction(cutAct)

        copyIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditCopy,
                                   QIcon(":/demos/documentviewer/images/copy.png"))
        copyAct = QAction(copyIcon, "Copy", self)
        copyAct.setShortcuts(QKeySequence.Copy)
        copyAct.setStatusTip("Copy the current selection's contents to the clipboard")
        copyAct.triggered.connect(self._textEdit.copy)
        editMenu.addAction(copyAct)
        editToolBar.addAction(copyAct)

        pasteIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditPaste,
                                    QIcon(":/demos/documentviewer/images/paste.png"))
        pasteAct = QAction(pasteIcon, "Paste", self)
        pasteAct.setShortcuts(QKeySequence.Paste)
        pasteAct.setStatusTip("Paste the clipboard's contents into the current selection")
        pasteAct.triggered.connect(self._textEdit.paste)
        editMenu.addAction(pasteAct)
        editToolBar.addAction(pasteAct)

        self.menuBar().addSeparator()

        cutAct.setEnabled(False)
        copyAct.setEnabled(False)
        self._textEdit.copyAvailable.connect(cutAct.setEnabled)
        self._textEdit.copyAvailable.connect(copyAct.setEnabled)

        self.openFile()

        self._textEdit.textChanged.connect(self._textChanged)
        self._uiAssets_back.triggered.connect(self._back)
        self._uiAssets_forward.triggered.connect(self._forward)

    @Slot()
    def _textChanged(self):
        self.maybeSetPrintingEnabled(self.hasContent())

    @Slot()
    def _back(self):
        bar = self._textEdit.verticalScrollBar()
        if bar.value() > bar.minimum():
            bar.setValue(bar.value() - 1)

    @Slot()
    def _forward(self):
        bar = self._textEdit.verticalScrollBar()
        if bar.value() < bar.maximum():
            bar.setValue(bar.value() + 1)

    def openFile(self):
        type = "open"
        file_name = QDir.toNativeSeparators(self._file.fileName())
        if not self._file.open(QFile.ReadOnly | QFile.Text):
            err = self._file.errorString()
            self.statusMessage(f"Cannot read file {file_name}:\n{err}.", type)
            return

        in_str = QTextStream(self._file)
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        if self._textEdit.toPlainText():
            self._textEdit.clear()
            self.disablePrinting()

        self._textEdit.setPlainText(in_str.readAll())
        QGuiApplication.restoreOverrideCursor()

        self.statusMessage(f"File {file_name} loaded.", type)
        self.maybeEnablePrinting()

    def hasContent(self):
        return bool(self._textEdit.toPlainText())

    def printDocument(self, printer):
        if not self.hasContent():
            return

        self._textEdit.print_(printer)

    def saveFile(self, file):
        file_name = QDir.toNativeSeparators(self._file.fileName())
        errorMessage = ""
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        if file.open(QFile.WriteOnly | QFile.Text):
            out = QTextStream(file)
            out << self._textEdit.toPlainText()
        else:
            error = file.errorString()
            errorMessage = f"Cannot open file {file_name} for writing:\n{error}."
        QGuiApplication.restoreOverrideCursor()

        if errorMessage:
            self.statusMessage(errorMessage)
            return False

        self.statusMessage(f"File {file_name} saved")
        return True

    def saveDocumentAs(self):
        dialog = QFileDialog(self.mainWindow())
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec() != QDialog.Accepted:
            return False

        files = dialog.selectedFiles()
        self._file.setFileName(files[0])
        return self.saveDocument()
