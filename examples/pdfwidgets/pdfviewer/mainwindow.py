# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import math
import sys

from PySide6.QtPdf import QPdfBookmarkModel, QPdfDocument, QPdfSearchModel
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (QDialog, QFileDialog, QLineEdit, QMainWindow, QMessageBox,
                               QSpinBox)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import QModelIndex, QPoint, QPointF, QStandardPaths, QUrl, Qt, Slot

from zoomselector import ZoomSelector
from searchresultdelegate import SearchResultDelegate
from ui_mainwindow import Ui_MainWindow


ZOOM_MULTIPLIER = math.sqrt(2.0)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.m_zoomSelector = ZoomSelector(self)
        self.m_pageSelector = QSpinBox(self)
        self.m_document = QPdfDocument(self)
        self.m_fileDialog = None

        self.ui.setupUi(self)

        self.m_zoomSelector.setMaximumWidth(150)
        self.ui.mainToolBar.insertWidget(self.ui.actionZoom_In, self.m_zoomSelector)

        self.ui.mainToolBar.insertWidget(self.ui.actionForward, self.m_pageSelector)
        self.m_pageSelector.valueChanged.connect(self.page_selected)
        nav = self.ui.pdfView.pageNavigator()
        nav.currentPageChanged.connect(self.m_pageSelector.setValue)
        nav.backAvailableChanged.connect(self.ui.actionBack.setEnabled)
        nav.forwardAvailableChanged.connect(self.ui.actionForward.setEnabled)

        self.m_zoomSelector.zoom_mode_changed.connect(self.ui.pdfView.setZoomMode)
        self.m_zoomSelector.zoom_factor_changed.connect(self.ui.pdfView.setZoomFactor)
        self.m_zoomSelector.reset()

        bookmark_model = QPdfBookmarkModel(self)
        bookmark_model.setDocument(self.m_document)

        self.ui.bookmarkView.setModel(bookmark_model)
        self.ui.bookmarkView.activated.connect(self.bookmark_selected)

        self.ui.thumbnailsView.setModel(self.m_document.pageModel())

        self.ui.pdfView.setDocument(self.m_document)

        self.ui.pdfView.zoomFactorChanged.connect(self.m_zoomSelector.set_zoom_factor)

        self.m_searchModel = QPdfSearchModel(self)
        self.m_searchModel.setDocument(self.m_document)
        self.m_searchField = QLineEdit(self)

        self.ui.pdfView.setSearchModel(self.m_searchModel)
        self.ui.searchToolBar.insertWidget(self.ui.actionFindPrevious, self.m_searchField)
        self.m_findShortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        self.m_findShortcut.activated.connect(self.setSearchFocus)
        self.m_searchField.setPlaceholderText("Find in document")
        self.m_searchField.setMaximumWidth(400)
        self.m_searchField.textEdited.connect(self.searchTextChanged)
        self.ui.searchResultsView.setModel(self.m_searchModel)
        self.m_delegate = SearchResultDelegate(self)
        self.ui.searchResultsView.setItemDelegate(self.m_delegate)
        sel_model = self.ui.searchResultsView.selectionModel()
        sel_model.currentChanged.connect(self.searchResultSelected)

    @Slot()
    def setSearchFocus(self):
        self.m_searchField.setFocus(Qt.FocusReason.ShortcutFocusReason)

    @Slot()
    def searchTextChanged(self, text):
        self.m_searchModel.setSearchString(text)
        self.ui.tabWidget.setCurrentWidget(self.ui.searchResultsTab)

    @Slot(QModelIndex, QModelIndex)
    def searchResultSelected(self, current, previous):
        if not current.isValid():
            return
        page = current.data(QPdfSearchModel.Role.Page.value)
        location = current.data(QPdfSearchModel.Role.Location.value)
        self.ui.pdfView.pageNavigator().jump(page, location)
        self.ui.pdfView.setCurrentSearchResultIndex(current.row())

    @Slot(QUrl)
    def open(self, doc_location):
        if doc_location.isLocalFile():
            self.m_document.load(doc_location.toLocalFile())
            document_title = self.m_document.metaData(QPdfDocument.MetaDataField.Title)
            self.setWindowTitle(document_title if document_title else "PDF Viewer")
            self.page_selected(0)
            self.m_pageSelector.setMaximum(self.m_document.pageCount() - 1)
        else:
            message = f"{doc_location} is not a valid local file"
            print(message, file=sys.stderr)
            QMessageBox.critical(self, "Failed to open", message)

    @Slot(QModelIndex)
    def bookmark_selected(self, index):
        if not index.isValid():
            return
        page = index.data(int(QPdfBookmarkModel.Role.Page))
        zoom_level = index.data(int(QPdfBookmarkModel.Role.Level))
        self.ui.pdfView.pageNavigator().jump(page, QPoint(), zoom_level)

    @Slot(int)
    def page_selected(self, page):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(page, QPoint(), nav.currentZoom())

    @Slot()
    def on_actionOpen_triggered(self):
        if not self.m_fileDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_fileDialog = QFileDialog(self, "Choose a PDF", directory)
            self.m_fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
            self.m_fileDialog.setMimeTypeFilters(["application/pdf"])
        if self.m_fileDialog.exec() == QDialog.Accepted:
            to_open = self.m_fileDialog.selectedUrls()[0]
            if to_open.isValid():
                self.open(to_open)

    @Slot()
    def on_actionFindNext_triggered(self):
        next = self.ui.searchResultsView.currentIndex().row() + 1
        if next >= self.m_searchModel.rowCount(QModelIndex()):
            next = 0
        self.ui.searchResultsView.setCurrentIndex(self.m_searchModel.index(next))

    @Slot()
    def on_actionFindPrevious_triggered(self):
        prev = self.ui.searchResultsView.currentIndex().row() - 1
        if prev < 0:
            prev = self.m_searchModel.rowCount(QModelIndex()) - 1
        self.ui.searchResultsView.setCurrentIndex(self.m_searchModel.index(prev))

    @Slot()
    def on_actionQuit_triggered(self):
        self.close()

    @Slot()
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About PdfViewer",
                          "An example using QPdfDocument")

    @Slot()
    def on_actionAbout_Qt_triggered(self):
        QMessageBox.aboutQt(self)

    @Slot()
    def on_actionZoom_In_triggered(self):
        factor = self.ui.pdfView.zoomFactor() * ZOOM_MULTIPLIER
        self.ui.pdfView.setZoomFactor(factor)

    @Slot()
    def on_actionZoom_Out_triggered(self):
        factor = self.ui.pdfView.zoomFactor() / ZOOM_MULTIPLIER
        self.ui.pdfView.setZoomFactor(factor)

    @Slot()
    def on_actionPrevious_Page_triggered(self):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(nav.currentPage() - 1, QPoint(), nav.currentZoom())

    @Slot()
    def on_actionNext_Page_triggered(self):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(nav.currentPage() + 1, QPoint(), nav.currentZoom())

    @Slot(QModelIndex)
    def on_thumbnailsView_activated(self, index):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(index.row(), QPointF(), nav.currentZoom())

    @Slot()
    def on_actionContinuous_triggered(self):
        cont_checked = self.ui.actionContinuous.isChecked()
        mode = QPdfView.PageMode.MultiPage if cont_checked else QPdfView.PageMode.SinglePage
        self.ui.pdfView.setPageMode(mode)

    @Slot()
    def on_actionBack_triggered(self):
        self.ui.pdfView.pageNavigator().back()

    @Slot()
    def on_actionForward_triggered(self):
        self.ui.pdfView.pageNavigator().forward()
