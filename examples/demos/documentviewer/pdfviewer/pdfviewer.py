# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from math import sqrt

from PySide6.QtWidgets import (QListView, QTreeView)
from PySide6.QtGui import QIcon, QKeySequence, QPainter
from PySide6.QtCore import (QDir, QIODevice, QModelIndex,
                            QPointF, Slot)
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtPdf import QPdfDocument, QPdfBookmarkModel
from PySide6.QtPdfWidgets import QPdfView, QPdfPageSelector

from abstractviewer import AbstractViewer
from pdfviewer.zoomselector import ZoomSelector


ZOOM_MULTIPLIER = sqrt(2.0)


class PdfViewer(AbstractViewer):

    def __init__(self):
        super().__init__()
        self.uiInitialized.connect(self.initPdfViewer)
        self._toolBar = None
        self._zoomSelector = None
        self._pageSelector = None
        self._document = None
        self._pdfView = None
        self._actionForward = None
        self._actionBack = None
        self._bookmarks = None
        self._pages = None

    def init(self, file, parent, mainWindow):
        self._pdfView = QPdfView(parent)
        super().init(file, self._pdfView, mainWindow)
        self._document = QPdfDocument(self)

    def supportedMimeTypes(self):
        return ["application/pdf"]

    def initPdfViewer(self):
        self._toolBar = self.addToolBar("PDF")
        self._zoomSelector = ZoomSelector(self._toolBar)

        nav = self._pdfView.pageNavigator()
        self._pageSelector = QPdfPageSelector(self._toolBar)
        self._toolBar.insertWidget(self._uiAssets_forward, self._pageSelector)
        self._pageSelector.setDocument(self._document)
        self._pageSelector.currentPageChanged.connect(self.pageSelected)
        nav.currentPageChanged.connect(self._pageSelector.setCurrentPage)
        nav.backAvailableChanged.connect(self._uiAssets_back.setEnabled)
        self._actionBack = self._uiAssets_back
        self._actionForward = self._uiAssets_forward
        self._uiAssets_back.triggered.connect(self.onActionBackTriggered)
        self._uiAssets_forward.triggered.connect(self.onActionForwardTriggered)

        self._toolBar.addSeparator()
        self._toolBar.addWidget(self._zoomSelector)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn,
                               QIcon(":/demos/documentviewer/images/zoom-in.png"))
        actionZoomIn = self._toolBar.addAction(icon, "Zoom in", QKeySequence.StandardKey.ZoomIn)
        actionZoomIn.setToolTip("Increase zoom level")
        actionZoomIn.triggered.connect(self.onActionZoomInTriggered)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut,
                               QIcon(":/demos/documentviewer/images/zoom-out.png"))
        actionZoomOut = self._toolBar.addAction(icon, "Zoom out", QKeySequence.StandardKey.ZoomOut)
        actionZoomOut.setToolTip("Decrease zoom level")
        actionZoomOut.triggered.connect(self.onActionZoomOutTriggered)

        nav.backAvailableChanged.connect(self._actionBack.setEnabled)
        nav.forwardAvailableChanged.connect(self._actionForward.setEnabled)

        self._zoomSelector.zoomModeChanged.connect(self._pdfView.setZoomMode)
        self._zoomSelector.zoomFactorChanged.connect(self._pdfView.setZoomFactor)
        self._zoomSelector.reset()

        bookmarkModel = QPdfBookmarkModel(self)
        bookmarkModel.setDocument(self._document)
        self._uiAssets_tabs.clear()
        self._bookmarks = QTreeView(self._uiAssets_tabs)
        self._bookmarks.activated.connect(self.bookmarkSelected)
        self._bookmarks.setModel(bookmarkModel)
        self._pdfView.setDocument(self._document)
        self._pdfView.setPageMode(QPdfView.PageMode.MultiPage)

        self.openPdfFile()
        if not self._document.pageCount():
            return

        self._pages = QListView(self._uiAssets_tabs)
        self._pages.setModel(self._document.pageModel())

        self._pages.selectionModel().currentRowChanged.connect(self._currentRowChanged)
        self._pdfView.pageNavigator().currentPageChanged.connect(self._pageChanged)

        self._uiAssets_tabs.addTab(self._pages, "Pages")
        self._uiAssets_tabs.addTab(self._bookmarks, "Bookmarks")

    def viewerName(self):
        return "PdfViewer"

    @Slot(QModelIndex, QModelIndex)
    def _currentRowChanged(self, current, previous):
        if previous == current:
            return

        nav = self._pdfView.pageNavigator()
        row = current.row()
        if nav.currentPage() == row:
            return
        nav.jump(row, QPointF(), nav.currentZoom())

    @Slot(int)
    def _pageChanged(self, page):
        if self._pages.currentIndex().row() == page:
            return
        self._pages.setCurrentIndex(self._pages.model().index(page, 0))

    @Slot()
    def openPdfFile(self):
        self.disablePrinting()

        if self._file.open(QIODevice.OpenModeFlag.ReadOnly):
            self._document.load(self._file)

        documentTitle = self._document.metaData(QPdfDocument.MetaDataField.Title)
        if not documentTitle:
            documentTitle = "PDF Viewer"
        self.statusMessage(documentTitle)
        self.pageSelected(0)

        file_name = QDir.toNativeSeparators(self._file.fileName())
        self.statusMessage(f"Opened PDF file {file_name}")
        self.maybeEnablePrinting()

    def hasContent(self):
        return self._document if self._document.pageCount() > 0 else False

    def supportsOverview(self):
        return True

    def printDocument(self, printer):
        if not self.hasContent():
            return

        painter = QPainter()
        painter.begin(printer)
        pageRect = printer.pageRect(QPrinter.Unit.DevicePixel).toRect()
        pageSize = pageRect.size()
        for i in range(0, self._document.pageCount()):
            if i > 0:
                printer.newPage()
            page = self._document.render(i, pageSize)
            painter.drawImage(pageRect, page)
        painter.end()

    @Slot(QModelIndex)
    def bookmarkSelected(self, index):
        if not index.isValid():
            return

        page = index.data(int(QPdfBookmarkModel.Role.Page))
        zoomLevel = index.data(int(QPdfBookmarkModel.Role.Level)).toReal()
        self._pdfView.pageNavigator().jump(page, QPointF(), zoomLevel)

    @Slot(int)
    def pageSelected(self, page):
        nav = self._pdfView.pageNavigator()
        nav.jump(page, QPointF(), nav.currentZoom())

    @Slot()
    def onActionZoomInTriggered(self):
        self._pdfView.setZoomFactor(self._pdfView.zoomFactor() * ZOOM_MULTIPLIER)

    @Slot()
    def onActionZoomOutTriggered(self):
        self._pdfView.setZoomFactor(self._pdfView.zoomFactor() / ZOOM_MULTIPLIER)

    @Slot()
    def onActionPreviousPageTriggered(self):
        nav = self._pdfView.pageNavigator()
        nav.jump(nav.currentPage() - 1, QPointF(), nav.currentZoom())

    @Slot()
    def onActionNextPageTriggered(self):
        nav = self._pdfView.pageNavigator()
        nav.jump(nav.currentPage() + 1, QPointF(), nav.currentZoom())

    @Slot()
    def onActionBackTriggered(self):
        self._pdfView.pageNavigator().back()

    @Slot()
    def onActionForwardTriggered(self):
        self._pdfView.pageNavigator().forward()
