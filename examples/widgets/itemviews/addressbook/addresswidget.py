
#############################################################################
##
## Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

try:
    import cpickle as pickle
except ImportError:
    import pickle

from PySide6.QtCore import (Qt, Signal, QRegularExpression, QModelIndex,
                            QItemSelection, QSortFilterProxyModel)
from PySide6.QtWidgets import QTabWidget, QMessageBox, QTableView, QAbstractItemView

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
        self._new_address_tab.send_details.connect(self.add_entry)

        self.addTab(self._new_address_tab, "Address Book")

        self.setup_tabs()

    def add_entry(self, name=None, address=None):
        """ Add an entry to the addressbook. """
        if name is None and address is None:
            add_dialog = AddDialogWidget()

            if add_dialog.exec():
                name = add_dialog.name
                address = add_dialog.address

        address = {"name": name, "address": address}
        addresses = self._table_model.addresses[:]

        # The QT docs for this example state that what we're doing here
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

            # Step 1: create the  row
            self._table_model.insertRows(0)

            # Step 2: get the index of the newly created row and use it.
            # to set the name
            ix = self._table_model.index(0, 0, QModelIndex())
            self._table_model.setData(ix, address["name"], Qt.EditRole)

            # Step 3: lather, rinse, repeat for the address.
            ix = self._table_model.index(0, 1, QModelIndex())
            self._table_model.setData(ix, address["address"], Qt.EditRole)

            # Remove the newAddressTab, as we now have at least one
            # address in the model.
            self.removeTab(self.indexOf(self._new_address_tab))

            # The screenshot for the QT example shows nicely formatted
            # multiline cells, but the actual application doesn't behave
            # quite so nicely, at least on Ubuntu. Here we resize the newly
            # created row so that multiline addresses look reasonable.
            table_view = self.currentWidget()
            table_view.resizeRowToContents(ix.row())

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
        ix = self._table_model.index(row, 0, QModelIndex())
        name = self._table_model.data(ix, Qt.DisplayRole)
        ix = self._table_model.index(row, 1, QModelIndex())
        address = self._table_model.data(ix, Qt.DisplayRole)

        # Open an addDialogWidget, and only allow the user to edit the address.
        add_dialog = AddDialogWidget()
        add_dialog.setWindowTitle("Edit a Contact")

        add_dialog._name_text.setReadOnly(True)
        add_dialog._name_text.setText(name)
        add_dialog._address_text.setText(address)

        # If the address is different, add it to the model.
        if add_dialog.exec():
            new_address = add_dialog.address
            if new_address != address:
                ix = self._table_model.index(row, 1, QModelIndex())
                self._table_model.setData(ix, new_address, Qt.EditRole)

    def remove_entry(self):
        """ Remove an entry from the addressbook. """
        table_view = self.currentWidget()
        proxy_model = table_view.model()
        selection_model = table_view.selectionModel()

        # Just like editEntry, but this time remove the selected row.
        indexes = selection_model.selectedRows()

        for index in indexes:
            row = proxy_model.mapToSource(index).row()
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
            table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
            table_view.horizontalHeader().setStretchLastSection(True)
            table_view.verticalHeader().hide()
            table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table_view.setSelectionMode(QAbstractItemView.SingleSelection)

            # This here be the magic: we use the group name (e.g. "ABC") to
            # build the regex for the QSortFilterProxyModel for the group's
            # tab. The regex will end up looking like "^[ABC].*", only
            # allowing this tab to display items where the name starts with
            # "A", "B", or "C". Notice that we set it to be case-insensitive.
            re = QRegularExpression(f"^[{group}].*")
            assert re.isValid()
            re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            proxy_model.setFilterRegularExpression(re)
            proxy_model.setFilterKeyColumn(0)  # Filter on the "name" column
            proxy_model.sort(0, Qt.AscendingOrder)

            # This prevents an application crash (see: http://www.qtcentre.org/threads/58874-QListView-SelectionModel-selectionChanged-Crash)
            viewselectionmodel = table_view.selectionModel()
            table_view.selectionModel().selectionChanged.connect(self.selection_changed)

            self.addTab(table_view, group)

    # Note: the QT example uses a QDataStream for the saving and loading.
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

        if len(addresses) == 0:
            QMessageBox.information(self, f"No contacts in file: {filename}")
        else:
            for address in addresses:
                self.add_entry(address["name"], address["address"])

    def write_to_file(self, filename):
        """ Save all contacts in the model to a file. """
        try:
            f = open(filename, "wb")
            pickle.dump(self._table_model.addresses, f)

        except IOError:
            QMessageBox.information(self, f"Unable to open file: {filename}")
        finally:
            f.close()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    address_widget = AddressWidget()
    address_widget.show()
    sys.exit(app.exec())
