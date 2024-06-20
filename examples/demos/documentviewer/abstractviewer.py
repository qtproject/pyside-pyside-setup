# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject

from PySide6.QtWidgets import (QDialog, QMenu)
from PySide6.QtCore import Signal, Slot
from PySide6.QtPrintSupport import QPrinter, QPrintDialog


MENU_NAME = "qtFileMenu"


class AbstractViewer(QObject):

    uiInitialized = Signal()
    printingEnabledChanged = Signal(bool)
    showMessage = Signal(str, int)
    documentLoaded = Signal(str)

    def __init__(self):
        super().__init__()
        self._file = None
        self._widget = None
        self._menus = []
        self._toolBars = []
        self._printingEnabled = False
        self._actions = []
        self._fileMenu = None

    def __del__(self):
        self.cleanup()

    def viewerName(self):
        return ""

    def saveState(self):
        return False

    def restoreState(self, state):
        return False

    def supportedMimeTypes():
        return []

    def init(self, file, widget, mainWindow):
        self._file = file
        self._widget = widget
        self._uiAssets_mainWindow = mainWindow

    def isEmpty(self):
        return not self.hasContent()

    def isPrintingEnabled(self):
        return self._printingEnabled

    def hasContent(self):
        return False

    def supportsOverview(self):
        return False

    def isModified(self):
        return False

    def saveDocument(self):
        return False

    def saveDocumentAs(self):
        return False

    def actions(self):
        return self._actions

    def widget(self):
        return self._widget

    def menus(self):
        return self._menus

    def mainWindow(self):
        return self._uiAssets_mainWindow

    def statusBar(self):
        return self.mainWindow().statusBar()

    def menuBar(self):
        return self.mainWindow().menuBar()

    def maybeEnablePrinting(self):
        self.maybeSetPrintingEnabled(True)

    def disablePrinting(self):
        self.maybeSetPrintingEnabled(False)

    def isDefaultViewer(self):
        return False

    def viewer(self):
        return self

    def statusMessage(self, message, type="", timeout=8000):
        msg = self.viewerName()
        if type:
            msg += "/" + type
        msg += ": " + message
        self.showMessage.emit(msg, timeout)

    def addToolBar(self, title):
        bar = self.mainWindow().addToolBar(title)
        name = title.replace(' ', '')
        bar.setObjectName(name)
        self._toolBars.append(bar)
        return bar

    def addMenu(self, title):
        menu = QMenu(title, self.menuBar())
        menu.setObjectName(title)
        self.menuBar().insertMenu(self._uiAssets_help, menu)
        self._menus.append(menu)
        return menu

    def cleanup(self):
        # delete all objects created by the viewer which need to be displayed
        # and therefore parented on MainWindow
        if self._file:
            self._file = None
        self._menus.clear()
        self._toolBars.clear()

    def fileMenu(self):
        if self._fileMenu:
            return self._fileMenu

        menus = self.mainWindow().findChildren(QMenu)
        for menu in menus:
            if menu.objectName() == MENU_NAME:
                self._fileMenu = menu
                return self._fileMenu
        self._fileMenu = self.addMenu("File")
        self._fileMenu.setObjectName(MENU_NAME)
        return self._fileMenu

    @Slot()
    def print_(self):
        type = "Printing"
        if not self.hasContent():
            self.statusMessage("No content to print.", type)
            return
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self.mainWindow())
        dlg.setWindowTitle("Print Document")
        if dlg.exec() == QDialog.Accepted:
            self.printDocument(printer)
        else:
            self.statusMessage("Printing canceled!", type)
            return
        state = printer.printerState()
        message = self.viewerName() + " :"
        if state == QPrinter.PrinterState.Aborted:
            message += "Printing aborted."
        elif state == QPrinter.PrinterState.Active:
            message += "Printing active."
        elif state == QPrinter.PrinterState.Idle:
            message += "Printing completed."
        elif state == QPrinter.PrinterState.Error:
            message += "Printing error."
        self.statusMessage(message, type)

    def maybeSetPrintingEnabled(self, enabled):
        if enabled == self._printingEnabled:
            return
        self._printingEnabled = enabled
        self.printingEnabledChanged.emit(enabled)

    def initViewer(self, back, forward, help, tabs):
        self._uiAssets_back = back
        self._uiAssets_forward = forward
        self._uiAssets_help = help
        self._uiAssets_tabs = tabs
        # Tabs can be populated individually by the viewer, if it
        # supports overview
        tabs.clear()
        tabs.setVisible(self.supportsOverview())
        self.uiInitialized.emit()
