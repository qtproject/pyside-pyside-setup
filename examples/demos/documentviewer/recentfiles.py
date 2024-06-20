# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import QFileInfo, QObject, QSettings, Signal, Slot


DEFAULT_MAX_FILES = 10


# Test if file exists and can be opened
def testFileAccess(fileName):
    return QFileInfo(fileName).isReadable()


class RemoveReason(Enum):
    Other = auto()
    Duplicate = auto()


class EmitPolicy(Enum):
    EmitWhenChanged = auto(),
    NeverEmit = auto()


s_maxFiles = "maxFiles"
s_openMode = "openMode"
s_fileNames = "fileNames"
s_file = "file"


class RecentFiles(QObject):

    countChanged = Signal(int)
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._maxFiles = DEFAULT_MAX_FILES
        self._files = []

    # Access to QStringList member functions
    def recentFiles(self):
        return self._files

    def isEmpty(self):
        return not self._files

    # Properties
    def maxFiles(self):
        return self._maxFiles

    def setMaxFiles(self, maxFiles):
        self._maxFiles = maxFiles

    def addFile(self, fileName):
        self._addFile(fileName, EmitPolicy.EmitWhenChanged)

    def removeFile(self, fileName):
        idx = self._files.find(fileName)
        self._removeFile(idx, RemoveReason.Other)

    @Slot()
    def clear(self):
        if self.isEmpty():
            return
        self._files.clear()
        self.countChanged.emit(0)

    def _addFile(self, fileName, policy):
        if not testFileAccess(fileName):
            return

        # Remember size, as cleanup can result in a change without size change
        c = len(self._files)

        # Clean dangling and duplicate files
        i = 0
        while i < len(self._files):
            file = self._files[i]
            if not testFileAccess(file):
                self._removeFile(file, RemoveReason.Other)
            elif file == fileName:
                self._removeFile(file, RemoveReason.Duplicate)
            else:
                i += 1

        # Cut tail
        while len(self._files) > self._maxFiles:
            self.removeFile((len(self._files) - 1), RemoveReason.Other)

        self._files.insert(0, fileName)

        if policy == EmitPolicy.NeverEmit:
            return

        if policy == EmitPolicy.EmitWhenChanged:
            self.changed.emit()
            if c != len(self._files):
                self.countChanged.emit(len(self._files))

    @Slot(list)
    def addFiles(self, files):
        if files.isEmpty():
            return

        if len(files) == 1:
            self.addFile(files[0])
            return

        c = len(self._files)

        for file in files:
            self.addFile(file, EmitPolicy.NeverEmit)

        self.changed.emit()
        if len(self._files) != c:
            self.countChanged.emit(len(self._files))

    def _removeFile(self, p, reason):
        index = p
        if isinstance(p, str):
            index = self._files.index(p) if p in self._files else -1
        if index < 0 or index >= len(self._files):
            return
        del self._files[index]

        # No emit for duplicate removal, add emits changed later.
        if reason != RemoveReason.Duplicate:
            self.changed.emit()

    @Slot(QSettings, str)
    def saveSettings(self, settings, key):
        settings.beginGroup(key)
        settings.setValue(s_maxFiles, self.maxFiles())
        if self._files:
            settings.beginWriteArray(s_fileNames, len(self._files))
            for index, file in enumerate(self._files):
                settings.setArrayIndex(index)
                settings.setValue(s_file, file)
            settings.endArray()
        settings.endGroup()

    @Slot(QSettings, str)
    def restoreFromSettings(self, settings, key):
        settings.beginGroup(key)
        self.setMaxFiles(settings.value(s_maxFiles, DEFAULT_MAX_FILES, int))
        self._files.clear()  # clear list without emitting
        numberFiles = settings.beginReadArray(s_fileNames)
        for index in range(0, numberFiles):
            settings.setArrayIndex(index)
            absoluteFilePath = settings.value(s_file)
            self._addFile(absoluteFilePath, EmitPolicy.NeverEmit)
        settings.endArray()
        settings.endGroup()
        if self._files:
            self.changed.emit()
        return True
