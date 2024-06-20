# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import (QDialog, QFileDialog, QMainWindow, QMessageBox)
from PySide6.QtCore import (QDir, QFile, QFileInfo, QSettings, Slot)

from ui_mainwindow import Ui_MainWindow
from viewerfactory import ViewerFactory
from recentfiles import RecentFiles
from recentfilemenu import RecentFileMenu


settingsDir = "WorkingDir"
settingsMainWindow = "MainWindow"
settingsViewers = "Viewers"
settingsFiles = "RecentFiles"


ABOUT_TEXT = """A Widgets application to display and print JSON,
text and PDF files. Demonstrates various features to use
in widget applications: Using QSettings, query and save
user preferences, manage file histories and control cursor
behavior when hovering over widgets.

"""


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()

        self._currentDir = QDir()
        self._viewer = None
        self._recentFiles = RecentFiles()

        self.ui.setupUi(self)
        self.ui.actionOpen.triggered.connect(self.onActionOpenTriggered)
        self.ui.actionAbout.triggered.connect(self.onActionAboutTriggered)
        self.ui.actionAboutQt.triggered.connect(self.onActionAboutQtTriggered)

        self._recentFiles = RecentFiles(self.ui.actionRecent)
        self._recentFiles.countChanged.connect(self._recentFilesCountChanged)

        self.readSettings()
        self._factory = ViewerFactory(self.ui.viewArea, self)
        viewers = ", ".join(self._factory.viewerNames())
        self.statusBar().showMessage(f'Available viewers: {viewers}')

        menu = RecentFileMenu(self, self._recentFiles)
        self.ui.actionRecent.setMenu(menu)
        menu.fileOpened.connect(self.openFile)
        button = self.ui.mainToolBar.widgetForAction(self.ui.actionRecent)
        if button:
            self.ui.actionRecent.triggered.connect(button.showMenu)

    @Slot(int)
    def _recentFilesCountChanged(self, count):
        self.ui.actionRecent.setText(f"{count} recent files")

    def closeEvent(self, event):
        self.saveSettings()

    @Slot(int)
    def onActionOpenTriggered(self):
        fileDialog = QFileDialog(self, "Open Document",
                                 self._currentDir.absolutePath())
        while (fileDialog.exec() == QDialog.Accepted
               and not self.openFile(fileDialog.selectedFiles()[0])):
            pass

    @Slot(str)
    def openFile(self, fileName):
        file = QFile(fileName)
        if not file.exists():
            nf = QDir.toNativeSeparators(fileName)
            self.statusBar().showMessage(f"File {nf} could not be opened")
            return False

        fileInfo = QFileInfo(file)
        self._currentDir = fileInfo.dir()
        self._recentFiles.addFile(fileInfo.absoluteFilePath())

        # If a viewer is already open, clean it up and save its settings
        self.resetViewer()
        self._viewer = self._factory.viewer(file)
        if not self._viewer:
            nf = QDir.toNativeSeparators(fileName)
            self.statusBar().showMessage(f"File {nf} can't be opened.")
            return False

        self.ui.actionPrint.setEnabled(self._viewer.hasContent())
        self._viewer.printingEnabledChanged.connect(self.ui.actionPrint.setEnabled)
        self.ui.actionPrint.triggered.connect(self._viewer.print_)
        self._viewer.showMessage.connect(self.statusBar().showMessage)

        self._viewer.initViewer(self.ui.actionBack, self.ui.actionForward,
                                self.ui.menuHelp.menuAction(),
                                self.ui.tabWidget)
        self.restoreViewerSettings()
        self.ui.scrollArea.setWidget(self._viewer.widget())
        return True

    @Slot()
    def onActionAboutTriggered(self):
        viewerNames = ", ".join(self._factory.viewerNames())
        mimeTypes = '\n'.join(self._factory.supportedMimeTypes())
        text = ABOUT_TEXT
        text += f"\nThis version has loaded the following plugins:\n{viewerNames}\n"
        text += f"\n\nIt supports the following mime types:\n{mimeTypes}"

        defaultViewer = self._factory.defaultViewer()
        if defaultViewer:
            n = defaultViewer.viewerName()
            text += f"\n\nOther mime types will be displayed with {n}."

        QMessageBox.about(self, "About Document Viewer Demo", text)

    @Slot()
    def onActionAboutQtTriggered(self):
        QMessageBox.aboutQt(self)

    def readSettings(self):
        settings = QSettings()

        # Restore working directory
        if settings.contains(settingsDir):
            self._currentDir = QDir(settings.value(settingsDir))
        else:
            self._currentDir = QDir.current()

        # Restore QMainWindow state
        if settings.contains(settingsMainWindow):
            mainWindowState = settings.value(settingsMainWindow)
            self.restoreState(mainWindowState)

        # Restore recent files
        self._recentFiles.restoreFromSettings(settings, settingsFiles)

    def saveSettings(self):
        settings = QSettings()

        # Save working directory
        settings.setValue(settingsDir, self._currentDir.absolutePath())

        # Save QMainWindow state
        settings.setValue(settingsMainWindow, self.saveState())

        # Save recent files
        self._recentFiles.saveSettings(settings, settingsFiles)

        settings.sync()

    def saveViewerSettings(self):
        if not self._viewer:
            return
        settings = QSettings()
        settings.beginGroup(settingsViewers)
        settings.setValue(self._viewer.viewerName(), self._viewer.saveState())
        settings.endGroup()
        settings.sync()

    def resetViewer(self):
        if not self._viewer:
            return
        self.saveViewerSettings()
        self._viewer.cleanup()

    def restoreViewerSettings(self):
        if not self._viewer:
            return
        settings = QSettings()
        settings.beginGroup(settingsViewers)
        viewerSettings = settings.value(self._viewer.viewerName())
        settings.endGroup()
        if viewerSettings:
            self._viewer.restoreState(viewerSettings)
