# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QBitArray, Qt, Signal, Slot


class Column(IntEnum):
    NUM_COLUMN = 0
    COILS_COLUMN = 1
    HOLDING_COLUMN = 2
    COLUMN_COUNT = 3
    ROW_COUNT = 10


class WriteRegisterModel(QAbstractTableModel):

    update_viewport = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_coils = QBitArray(Column.ROW_COUNT, False)
        self.m_number = 0
        self.m_address = 0
        self.m_holdingRegisters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def rowCount(self, parent):
        return Column.ROW_COUNT

    def columnCount(self, parent):
        return Column.COLUMN_COUNT

    def data(self, index, role):
        row = index.row()
        column = index.column()
        if not index.isValid() or row >= Column.ROW_COUNT or column >= Column.COLUMN_COUNT:
            return None

        assert self.m_coils.size() == Column.ROW_COUNT
        assert len(self.m_holdingRegisters) == Column.ROW_COUNT

        if column == Column.NUM_COLUMN and role == Qt.ItemDataRole.DisplayRole:
            return f"{row}"

        if column == Column.COILS_COLUMN and role == Qt.ItemDataRole.CheckStateRole:  # coils
            return Qt.Checked if self.m_coils[row] else Qt.Unchecked

        # holding registers
        if column == Column.HOLDING_COLUMN and role == Qt.ItemDataRole.DisplayRole:
            reg = self.m_holdingRegisters[row]
            return f"0x{reg:x}"
        return None

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section == Column.NUM_COLUMN:
                return "#"
            if section == Column.COILS_COLUMN:
                return "Coils "
            if section == Column.HOLDING_COLUMN:
                return "Holding Registers"
        return None

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()
        if not index.isValid() or row >= Column.ROW_COUNT or column >= Column.COLUMN_COUNT:
            return False

        assert self.m_coils.size() == Column.ROW_COUNT
        assert len(self.m_holdingRegisters) == Column.ROW_COUNT

        if column == Column.COILS_COLUMN and role == Qt.ItemDataRole.CheckStateRole:  # coils
            s = Qt.CheckState(int(value))
            if s == Qt.Checked:
                self.m_coils.setBit(row)
            else:
                self.m_coils.clearBit(row)
            self.dataChanged.emit(index, index)
            return True

        if column == Column.HOLDING_COLUMN and role == Qt.ItemDataRole.EditRole:
            # holding registers
            base = 16 if value.startswith("0x") else 10
            self.m_holdingRegisters[row] = int(value, base=base)
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        row = index.row()
        column = index.column()
        flags = super().flags(index)
        if not index.isValid() or row >= Column.ROW_COUNT or column >= Column.COLUMN_COUNT:
            return flags

        if row < self.m_address or row >= (self.m_address + self.m_number):
            flags &= ~Qt.ItemIsEnabled

        if column == Column.COILS_COLUMN:  # coils
            return flags | Qt.ItemIsUserCheckable
        if column == Column.HOLDING_COLUMN:  # holding registers
            return flags | Qt.ItemIsEditable
        return flags

    @Slot(int)
    def set_start_address(self, address):
        self.m_address = address
        self.update_viewport.emit()

    @Slot(str)
    def set_number_of_values(self, number):
        self.m_number = int(number)
        self.update_viewport.emit()
