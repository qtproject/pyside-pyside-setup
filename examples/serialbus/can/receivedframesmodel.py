# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSize, Qt


class ReceivedFramesModelColumns(IntEnum):
    number = 0
    timestamp = 1
    flags = 2
    can_id = 3
    DLC = 4
    data = 5
    count = 6


clipboard_text_role = Qt.ItemDataRole.UserRole + 1


column_alignment = [Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    Qt.AlignmentFlag.AlignCenter,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter]


class ReceivedFramesModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_framesQueue = []  # QQueue()
        self.m_framesAccumulator = []
        self.m_queueLimit = 0

    def remove_rows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.m_framesQueue = self.m_framesQueue[0:row] + self.m_framesQueue[row + count:]
        self.endRemoveRows()
        return True

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == ReceivedFramesModelColumns.number:
                return "#"
            if section == ReceivedFramesModelColumns.timestamp:
                return "Timestamp"
            if section == ReceivedFramesModelColumns.flags:
                return "Flags"
            if section == ReceivedFramesModelColumns.can_id:
                return "CAN-ID"
            if section == ReceivedFramesModelColumns.DLC:
                return "DLC"
            if section == ReceivedFramesModelColumns.data:
                return "Data"

        if role == Qt.ItemDataRole.SizeHintRole and orientation == Qt.Orientation.Horizontal:
            if section == ReceivedFramesModelColumns.number:
                return QSize(80, 25)
            if section == ReceivedFramesModelColumns.timestamp:
                return QSize(130, 25)
            if section == ReceivedFramesModelColumns.flags:
                return QSize(25, 25)
            if section == ReceivedFramesModelColumns.can_id:
                return QSize(50, 25)
            if section == ReceivedFramesModelColumns.DLC:
                return QSize(25, 25)
            if section == ReceivedFramesModelColumns.data:
                return QSize(200, 25)
        return None

    def data(self, index, role):
        if not self.m_framesQueue:
            return None
        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return column_alignment[index.column()]
        if role == Qt.ItemDataRole.AlignmentFlag.DisplayRole:
            return self.m_framesQueue[row][column]
        if role == clipboard_text_role:
            f = self.m_framesQueue[row][column]
            return f"[{f}]" if column == ReceivedFramesModelColumns.DLC else f
        return None

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.m_framesQueue)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else ReceivedFramesModelColumns.count

    def append_frames(self, slvector):
        self.m_framesAccumulator.extend(slvector)

    def need_update(self):
        return self.m_framesAccumulator

    def update(self):
        if not self.m_framesAccumulator:
            return

        if self.m_queueLimit:
            self.append_frames_ring_buffer(self.m_framesAccumulator)
        else:
            self.append_frames_unlimited(self.m_framesAccumulator)
        self.m_framesAccumulator.clear()

    def append_frames_ring_buffer(self, slvector):
        slvector_len = len(slvector)
        row_count = self.rowCount()
        if self.m_queueLimit <= row_count + slvector_len:
            if slvector_len < self.m_queueLimit:
                self.remove_rows(0, row_count + slvector_len - self.m_queueLimit + 1)
            else:
                self.clear()

        self.beginInsertRows(QModelIndex(), row_count, row_count + slvector_len - 1)
        if slvector_len < self.m_queueLimit:
            self.m_framesQueue.extend(slvector)
        else:
            self.m_framesQueue.extend(slvector[slvector_len - self.m_queueLimit:])
        self.endInsertRows()

    def append_frame(self, slist):
        self.append_frames([slist])

    def append_frames_unlimited(self, slvector):
        row_count = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_count, row_count + len(slvector) - 1)
        self.m_framesQueue.extend(slvector)
        self.endInsertRows()

    def clear(self):
        if self.m_framesQueue:
            self.beginResetModel()
            self.m_framesQueue.clear()
            self.endResetModel()

    def set_queue_limit(self, limit):
        self.m_queueLimit = limit
        frame_queue_len = len(self.m_framesQueue)
        if limit and frame_queue_len > limit:
            self.remove_rows(0, frame_queue_len - limit)
