#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
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

from PySide6.QtCore import (QCoreApplication, QDir, QRegularExpression, Qt,
                            Property, Slot)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                               QFormLayout, QGroupBox, QHBoxLayout,
                               QInputDialog, QLineEdit, QListWidget,
                               QListWidgetItem, QPushButton, QVBoxLayout,
                               QWidget)


DEFAULT_TYPES = ['int', 'str', 'PySide6.QtCore.QPoint', 'PySide6.QtCore.QRect',
                 'PySide6.QtCore.QSize', 'PySide6.QtGui.QColor']


FUNCTION_PATTERN = r'^\w+\([\w ,]*\)$'


class ValidatingInputDialog(QDialog):
    """A dialog for text input with a regular expression validation."""
    def __init__(self, label, pattern, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._lineedit = QLineEdit()
        self._lineedit.setClearButtonEnabled(True)
        re = QRegularExpression(pattern)
        assert(re.isValid())
        self._validator = QRegularExpressionValidator(re, self)
        self._lineedit.setValidator(self._validator)
        self._form_layout.addRow(label, self._lineedit)
        layout.addLayout(self._form_layout)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)

    @Property(str)
    def text(self):
        return self._lineedit.text()

    @text.setter
    def text(self, t):
        self._lineedit.setText(t)

    @Property(str)
    def placeholder_text(self):
        return self._lineedit.placeholderText()

    @placeholder_text.setter
    def placeholder_text(self, t):
        self._lineedit.setPlaceholderText(t)

    @Property(int)
    def cursor_position(self):
        return self._lineedit.cursorPosition()

    @cursor_position.setter
    def cursor_position(self, p):
        self._lineedit.setCursorPosition(p)

    def is_valid(self):
        return self.text

    def accept(self):
        if self.is_valid():
            super(ValidatingInputDialog, self).accept()


class FunctionSignatureDialog(ValidatingInputDialog):
    """A dialog for input of function signatures."""
    def __init__(self, name, parent=None):
        super().__init__(name, FUNCTION_PATTERN, parent)
        self.text = '()'
        self.cursor_position = 0


class PropertyDialog(ValidatingInputDialog):
    """A dialog for input of a property name and type."""
    def __init__(self, parent=None):
        super().__init__('&Name:', r'^\w+$', parent)
        self.setWindowTitle('Add a Property')
        self._type_combo = QComboBox()
        self._type_combo.addItems(DEFAULT_TYPES)
        self._form_layout.insertRow(0, '&Type:', self._type_combo)

    def property_type(self):
        return self._type_combo.currentText()


class ListChooser(QGroupBox):
    """A widget for editing a list of strings with a customization point
       for creating the strings."""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        main_layout = QHBoxLayout(self)
        self._list = QListWidget(self)
        self._list.currentItemChanged.connect(self._current_item_changed)
        main_layout.addWidget(self._list)

        vbox_layout = QVBoxLayout()
        main_layout.addLayout(vbox_layout)
        self._addButton = QPushButton("Add...")
        vbox_layout.addWidget(self._addButton)
        self._addButton.clicked.connect(self._add)
        self._removeButton = QPushButton("Remove")
        self._removeButton.setEnabled(False)
        self._removeButton.clicked.connect(self._remove_current)
        vbox_layout.addWidget(self._removeButton)
        vbox_layout.addStretch()

    @Property(list)
    def items(self):
        result = []
        for i in range(self._list.count()):
            result.append(self._list.item(i).text())
        return result

    @items.setter
    def items(self, item_list):
        self._list.clear()
        for i in item_list:
            self._list.append(i)

    @Slot(QListWidgetItem, QListWidgetItem)
    def _current_item_changed(self, current, previous):
        self._removeButton.setEnabled(current is not None)

    @Slot()
    def _add(self):
        new_item = self._create_new_item()
        if new_item:
            self._list.addItem(new_item)

    def _create_new_item(self):
        """Overwrite to return a new item."""
        return 'new_item'

    @Slot()
    def _remove_current(self):
        row = self._list.row(self._list.currentItem())
        if row >= 0:
            self._list.takeItem(row)


class SignalChooser(ListChooser):
    """A widget for editing a list of signal function signatures."""
    def __init__(self, parent=None):
        super().__init__('Signals', parent)

    def _create_new_item(self):
        dialog = FunctionSignatureDialog('&Signal signature:', self)
        dialog.setWindowTitle('Enter Signal')
        if dialog.exec() != QDialog.Accepted:
            return ''
        return dialog.text


class PropertyChooser(ListChooser):
    """A widget for editing a list of properties as a string of 'type name'."""
    def __init__(self, parent=None):
        super().__init__('Properties', parent)

    def _create_new_item(self):
        dialog = PropertyDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return ''
        name = dialog.text
        property_type = dialog.property_type()
        return f'{property_type} {name}'
