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
        self._textEdit = None
        self.uiInitialized.connect(self.setupTxtUi)

        cutIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditCut,
                                  QIcon(":/demos/documentviewer/images/cut.png"))
        self._cutAct = QAction(self)
        self._cutAct.setText(self.tr("Cut"))
        self._cutAct.setIcon(cutIcon)
        self._cutAct.setShortcuts(QKeySequence.StandardKey.Cut)
        self._cutAct.setStatusTip(self.tr("Cut the current selection's contents to the clipboard"))

        copyIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditCopy,
                                   QIcon(":/demos/documentviewer/images/copy.png"))
        self._copyAct = QAction(self)
        self._copyAct.setText(self.tr("Copy"))
        self._copyAct.setIcon(copyIcon)
        self._copyAct.setShortcuts(QKeySequence.StandardKey.Copy)
        self._copyAct.setStatusTip(self.tr("Copy the current selection's contents to the clipboard"))  # noqa: E501

        pasteIcon = QIcon.fromTheme(QIcon.ThemeIcon.EditPaste,
                                    QIcon(":/demos/documentviewer/images/paste.png"))
        self._pasteAct = QAction(self)
        self._pasteAct.setText(self.tr("Paste"))
        self._pasteAct.setIcon(pasteIcon)
        self._pasteAct.setShortcuts(QKeySequence.StandardKey.Paste)
        self._pasteAct.setStatusTip(self.tr("Paste the clipboard's contents into the current selection"))  # noqa: E501

    def init(self, file, parent, mainWindow):
        self._textEdit = QPlainTextEdit(parent)
        super().init(file, self._textEdit, mainWindow)

    def viewerName(self):
        return "TxtViewer"

    def cleanup(self):
        del self._textEdit
        self._textEdit = None
        super().cleanup()

    def supportedMimeTypes(self):
        return ["text/plain"]

    def retranslate(self):
        if not self._toolBars:
            return
        self._menus[0].setTitle(self.tr("Edit"))
        self._toolBars[0].setWindowTitle(self.tr("Edit"))
        self._cutAct.setText(self.tr("C&ut"))
        self._copyAct.setText(self.tr("&Copy"))
        self._pasteAct.setText(self.tr("&Paste"))

    @Slot()
    def setupTxtUi(self):
        editMenu = self.addMenu()
        editToolBar = self.addToolBar()
        editMenu.addAction(self._cutAct)
        editToolBar.addAction(self._cutAct)
        editMenu.addAction(self._copyAct)
        editToolBar.addAction(self._copyAct)
        editMenu.addAction(self._pasteAct)
        editToolBar.addAction(self._pasteAct)

        self.menuBar().addSeparator()

        self._cutAct.setEnabled(False)
        self._copyAct.setEnabled(False)
        self._cutAct.triggered.connect(self._textEdit.cut)
        self._copyAct.triggered.connect(self._textEdit.copy)
        self._pasteAct.triggered.connect(self._textEdit.paste)
        self._textEdit.copyAvailable.connect(self._cutAct.setEnabled)
        self._textEdit.copyAvailable.connect(self._copyAct.setEnabled)

        self.retranslate()
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
        if not self._file.open(QFile.OpenModeFlag.ReadOnly
                               | QFile.OpenModeFlag.Text):
            err = self._file.errorString()
            message = self.tr("Cannot read file {}:\n{}.").format(file_name, err)
            self.statusMessage(message, type)
            return

        in_str = QTextStream(self._file)
        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if self._textEdit.toPlainText():
            self._textEdit.clear()
            self.disablePrinting()

        self._textEdit.setPlainText(in_str.readAll())
        QGuiApplication.restoreOverrideCursor()

        self.statusMessage(self.tr("File {} loaded.").format(file_name), type)
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
        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if file.open(QFile.OpenModeFlag.WriteOnly | QFile.OpenModeFlag.Text):
            out = QTextStream(file)
            out << self._textEdit.toPlainText()
        else:
            error = file.errorString()
            errorMessage = self.tr("Cannot open file {} for writing:\n{}.").format(file_name, error)
        QGuiApplication.restoreOverrideCursor()

        if errorMessage:
            self.statusMessage(errorMessage)
            return False

        self.statusMessage(self.tr("File {} saved").format(file_name))
        return True

    def saveDocumentAs(self):
        dialog = QFileDialog(self.mainWindow())
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        files = dialog.selectedFiles()
        self._file.setFileName(files[0])
        return self.saveDocument()
