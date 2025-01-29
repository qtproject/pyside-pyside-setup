# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum, auto

from PySide6.QtWidgets import (QMessageBox)
from PySide6.QtCore import (QFileInfo, QMimeDatabase, QTimer)

from txtviewer.txtviewer import TxtViewer
from jsonviewer.jsonviewer import JsonViewer
from pdfviewer.pdfviewer import PdfViewer
from imageviewer.imageviewer import ImageViewer


class DefaultPolicy(Enum):
    NeverDefault = auto()
    DefaultToTxtViewer = auto()
    DefaultToCustomViewer = auto()


class ViewerFactory:

    def __init__(self, displayWidget, mainWindow,
                 policy=DefaultPolicy.NeverDefault):
        self._viewers = {}
        self._defaultViewer = None
        self._defaultWarning = True
        self._defaultPolicy = policy
        self._displayWidget = displayWidget
        self._mainWindow = mainWindow
        self._mimeTypes = []
        for v in [PdfViewer(), JsonViewer(), TxtViewer(), ImageViewer()]:
            self._viewers[v.viewerName()] = v
            if v.isDefaultViewer():
                self._defaultViewer = v

    def defaultPolicy(self):
        return self._defaultPolicy

    def setDefaultPolicy(self, policy):
        self._defaultPolicy = policy

    def defaultWarning(self):
        return self._defaultWarning

    def setDefaultWarning(self, on):
        self._defaultWarning = on

    def viewer(self, file):
        info = QFileInfo(file)
        db = QMimeDatabase()
        mimeType = db.mimeTypeForFile(info)

        viewer = self.viewerForMimeType(mimeType)
        if not viewer:
            print(f"Mime type {mimeType.name()} not supported.")
            return None

        viewer.init(file, self._displayWidget, self._mainWindow)
        return viewer

    def viewerNames(self, showDefault=False):
        if not showDefault:
            return self._viewers.keys()

        list = []
        for name, viewer in self._viewers.items():
            if ((self._defaultViewer and viewer.isDefaultViewer())
                    or (not self._defaultViewer and name == "TxtViewer")):
                name += "(default)"
            list.append(name)
        return list

    def viewers(self):
        return self._viewers.values()

    def findViewer(self, viewerName):
        for viewer in self.viewers():
            if viewer.viewerName() == viewerName:
                return viewer
        print(f"Plugin {viewerName} not loaded.")
        return None

    def viewerForMimeType(self, mimeType):
        for viewer in self.viewers():
            for type in viewer.supportedMimeTypes():
                if mimeType.inherits(type):
                    return viewer

        viewer = self.defaultViewer()

        if self._defaultWarning:
            mbox = QMessageBox()
            mbox.setIcon(QMessageBox.Warning)
            name = mimeType.name()
            viewer_name = viewer.viewerName()
            m = f"Mime type {name} not supported. Falling back to {viewer_name}."
            mbox.setText(m)
            mbox.setStandardButtons(QMessageBox.Ok)
            QTimer.singleShot(8000, mbox.close)
            mbox.exec()
        return viewer

    def defaultViewer(self):
        if self._defaultPolicy == DefaultPolicy.NeverDefault:
            return None
        if self._defaultPolicy == DefaultPolicy.DefaultToCustomViewer and self._defaultViewer:
            return self._defaultViewer
        return self.findViewer("TxtViewer")

    def supportedMimeTypes(self):
        if not self._mimeTypes:
            for viewer in self.viewers():
                self._mimeTypes.extend(viewer.supportedMimeTypes())
        return self._mimeTypes
