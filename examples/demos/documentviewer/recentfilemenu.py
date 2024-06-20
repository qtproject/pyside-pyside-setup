# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Signal, Slot


class RecentFileMenu(QMenu):
    fileOpened = Signal(str)

    def __init__(self, parent, recent):
        super().__init__(parent)
        self._recentFiles = recent
        self._recentFiles.changed.connect(self.updateList)
        self._recentFiles.destroyed.connect(self.deleteLater)
        self.updateList()

    @Slot()
    def updateList(self):
        for a in self.actions():
            del a

        if not self._recentFiles:
            self.addAction("<no recent files>")
            return

        for fileName in self._recentFiles.recentFiles():
            action = self.addAction(fileName)
            action.triggered.connect(self._emitFileOpened)

    @Slot()
    def _emitFileOpened(self):
        action = self.sender()
        self.fileOpened.emit(action.text())
