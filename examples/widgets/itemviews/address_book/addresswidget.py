# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

try:
    import cpickle as pickle
except ImportError:
    import pickle

from PySide6.QtCore import (QItemSelection, QRegularExpression, QSortFilterProxyModel,
                            Qt, Signal, Slot)
from PySide6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableView, QTabWidget

from tablemodel import TableModel
from newaddresstab import NewAddressTab
from adddialogwidget import AddDialogWidget


class AddressWidget(QTabWidget):
    """ The central widget of the application. Most of the addressbook's
        functionality is contained in this class.
    """

    selection_changed = Signal(QItemSelection)

    def __init__(self, parent=None):
        """ Initialize the AddressWidget. """
        super().__init__(parent)

        self._table_model = TableModel()
        self._new_address_tab = NewAddressTab()
        self._new_address_tab.triggered.connect(self.add_entry)

        self.addTab(self._new_address_tab, "Address Book")

        self.setup_tabs()

    @Slot()
    def add_entry(self):
        """ Add an entry to the addressbook. """
        add_dialog = AddDialogWidget(self)
        if add_dialog.exec() != QDialog.Accepted:
            return

        name = add_dialog.name
        address = {"name": name, "address": add_dialog.address}
        addresses = self._table_model.addresses[:]

        # The Qt docs for this example state that what we're doing here
        # is checking if the entered name already exists. What they
        # (and we here) are actually doing is checking if the whole
        # name/address pair exists already - ok for the purposes of this
        # example, but obviously not how a real addressbook application
        # should behave.
        try:
            addresses.remove(address)
            QMessageBox.information(self, "Duplicate Name",
                                    f'The name "{name}" already exists.')
        except ValueError:
            # The address didn't already exist, so let's add it to the model.

            self._add_entry(address)

            # Remove the newAddressTab, as we now have at least one
            # address in the model.
            self.removeTab(self.indexOf(self._new_address_tab))

            first_char = name[0:1].upper()
            for t in range(self.count()):
                if first_char in self.tabText(t)[0:1]:
                    self.setCurrentIndex(t)
                    break

    def _add_entry(self, address):
        # Step 1: create the  row
        self._table_model.insertRows(0)

        # Step 2: get the index of the newly created row and use it.
        # to set the name
        ix = self._table_model.index(0, 0)
        self._table_model.setData(ix, address["name"], Qt.ItemDataRole.EditRole)

        # Step 3: lather, rinse, repeat for the address.
        ix = self._table_model.index(0, 1)
        self._table_model.setData(ix, address["address"], Qt.ItemDataRole.EditRole)

    @Slot()
    def edit_entry(self):
        """ Edit an entry in the addressbook. """
        table_view = self.currentWidget()
        proxy_model = table_view.model()
        selection_model = table_view.selectionModel()

        # Get the name and address of the currently selected row.
        indexes = selection_model.selectedRows()
        if len(indexes) != 1:
            return

        row = proxy_model.mapToSource(indexes[0]).row()
        ix = self._table_model.index(row, 0)
        name = self._table_model.data(ix, Qt.ItemDataRole.DisplayRole)
        ix = self._table_model.index(row, 1)
        address = self._table_model.data(ix, Qt.ItemDataRole.DisplayRole)

        # Open an addDialogWidget, and only allow the user to edit the address.
        add_dialog = AddDialogWidget(self)
        add_dialog.setWindowTitle("Edit a Contact")

        add_dialog.name_enabled = False
        add_dialog.name = name
        add_dialog.address = address

        # If the address is different, add it to the model.
        if add_dialog.exec():
            new_address = add_dialog.address
            if new_address != address:
                ix = self._table_model.index(row, 1)
                self._table_model.setData(ix, new_address, Qt.ItemDataRole.EditRole)

    @Slot()
    def remove_entry(self):
        """ Remove an entry from the addressbook. """
        table_view = self.currentWidget()
        proxy_model = table_view.model()
        selection_model = table_view.selectionModel()

        # Just like editEntry, but this time remove the selected row.
        indexes = selection_model.selectedRows()
        if len(indexes) != 1:
            return

        row = proxy_model.mapToSource(indexes[0]).row()
        self._table_model.removeRows(row)

        # If we've removed the last address in the model, display the
        # newAddressTab
        if self._table_model.rowCount() == 0:
            self.insertTab(0, self._new_address_tab, "Address Book")

    def setup_tabs(self):
        """ Setup the various tabs in the AddressWidget. """
        groups = ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VW", "XYZ"]

        for group in groups:
            proxy_model = QSortFilterProxyModel(self)
            proxy_model.setSourceModel(self._table_model)
            proxy_model.setDynamicSortFilter(True)

            table_view = QTableView()
            table_view.setModel(proxy_model)
            table_view.setSortingEnabled(True)
            table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table_view.horizontalHeader().setStretchLastSection(True)
            table_view.verticalHeader().hide()
            table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

            # This here be the magic: we use the group name (e.g. "ABC") to
            # build the regex for the QSortFilterProxyModel for the group's
            # tab. The regex will end up looking like "^[ABC].*", only
            # allowing this tab to display items where the name starts with
            # "A", "B", or "C". Notice that we set it to be case-insensitive.
            re = QRegularExpression(f"^[{group}].*")
            assert re.isValid()
            re.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
            proxy_model.setFilterRegularExpression(re)
            proxy_model.setFilterKeyColumn(0)  # Filter on the "name" column
            proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

            table_view.selectionModel().selectionChanged.connect(self.selection_changed)

            self.addTab(table_view, group)

    # Note: the Qt example uses a QDataStream for the saving and loading.
    # Here we're using a python dictionary to store the addresses, which
    # can't be streamed using QDataStream, so we just use cpickle for this
    # example.
    def read_from_file(self, filename):
        """ Read contacts in from a file. """
        try:
            f = open(filename, "rb")
            addresses = pickle.load(f)
        except IOError:
            QMessageBox.information(self, f"Unable to open file: {filename}")
        finally:
            f.close()

        for address in addresses:
            self._add_entry(address)

        if addresses:
            self.removeTab(self.indexOf(self._new_address_tab))
        else:
            QMessageBox.information(self, f"No contacts in file: {filename}")

    def write_to_file(self, filename):
        """ Save all contacts in the model to a file. """
        try:
            f = open(filename, "wb")
            pickle.dump(self._table_model.addresses, f)

        except IOError:
            QMessageBox.information(self, f"Unable to open file: {filename}")
        finally:
            f.close()
