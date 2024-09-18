# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import (QAbstractItemView, QDataWidgetMapper,
                               QHeaderView, QMainWindow, QMessageBox)
from PySide6.QtGui import QKeySequence
from PySide6.QtSql import QSqlRelation, QSqlRelationalTableModel, QSqlTableModel
from PySide6.QtCore import Qt, Slot
import createdb
from ui_bookwindow import Ui_BookWindow
from bookdelegate import BookDelegate


class BookWindow(QMainWindow, Ui_BookWindow):
    """A window to show the books available"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize db
        createdb.init_db()

        model = QSqlRelationalTableModel(self.bookTable)
        model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        model.setTable("books")

        # Remember the indexes of the columns:
        author_idx = model.fieldIndex("author")
        genre_idx = model.fieldIndex("genre")

        # Set the relations to the other database tables:
        model.setRelation(author_idx, QSqlRelation("authors", "id", "name"))
        model.setRelation(genre_idx, QSqlRelation("genres", "id", "name"))

        # Set the localized header captions:
        model.setHeaderData(author_idx, Qt.Orientation.Horizontal, self.tr("Author Name"))
        model.setHeaderData(genre_idx, Qt.Orientation.Horizontal, self.tr("Genre"))
        model.setHeaderData(model.fieldIndex("title"), Qt.Orientation.Horizontal, self.tr("Title"))
        model.setHeaderData(model.fieldIndex("year"), Qt.Orientation.Horizontal, self.tr("Year"))
        model.setHeaderData(model.fieldIndex("rating"),
                            Qt.Orientation.Horizontal, self.tr("Rating"))

        if not model.select():
            print(model.lastError())

        # Set the model and hide the ID column:
        self.bookTable.setModel(model)
        self.bookTable.setItemDelegate(BookDelegate(self.bookTable))
        self.bookTable.setColumnHidden(model.fieldIndex("id"), True)
        self.bookTable.setSelectionMode(QAbstractItemView.SingleSelection)

        # Initialize the Author combo box:
        self.authorEdit.setModel(model.relationModel(author_idx))
        self.authorEdit.setModelColumn(model.relationModel(author_idx).fieldIndex("name"))

        self.genreEdit.setModel(model.relationModel(genre_idx))
        self.genreEdit.setModelColumn(model.relationModel(genre_idx).fieldIndex("name"))

        # Lock and prohibit resizing of the width of the rating column:
        self.bookTable.horizontalHeader().setSectionResizeMode(model.fieldIndex("rating"),
                                                               QHeaderView.ResizeToContents)

        mapper = QDataWidgetMapper(self)
        mapper.setModel(model)
        mapper.setItemDelegate(BookDelegate(self))
        mapper.addMapping(self.titleEdit, model.fieldIndex("title"))
        mapper.addMapping(self.yearEdit, model.fieldIndex("year"))
        mapper.addMapping(self.authorEdit, author_idx)
        mapper.addMapping(self.genreEdit, genre_idx)
        mapper.addMapping(self.ratingEdit, model.fieldIndex("rating"))

        selection_model = self.bookTable.selectionModel()
        selection_model.currentRowChanged.connect(mapper.setCurrentModelIndex)

        self.bookTable.setCurrentIndex(model.index(0, 0))
        self.create_menubar()

    def showError(self, err):
        QMessageBox.critical(self, "Unable to initialize Database",
                             f"Error initializing database: {err.text()}")

    def create_menubar(self):
        file_menu = self.menuBar().addMenu(self.tr("&File"))
        quit_action = file_menu.addAction(self.tr("&Quit"))
        quit_action.triggered.connect(qApp.quit)  # noqa: F821

        help_menu = self.menuBar().addMenu(self.tr("&Help"))
        about_action = help_menu.addAction(self.tr("&About"))
        about_action.setShortcut(QKeySequence.HelpContents)
        about_action.triggered.connect(self.about)
        aboutQt_action = help_menu.addAction("&About Qt")
        aboutQt_action.triggered.connect(qApp.aboutQt)  # noqa: F821

    @Slot()
    def about(self):
        QMessageBox.about(self, self.tr("About Books"),
                          self.tr("<p>The <b>Books</b> example shows how to use Qt SQL classes "
                          "with a model/view framework."))
