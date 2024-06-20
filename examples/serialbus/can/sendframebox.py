# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import re

from PySide6.QtGui import QValidator
from PySide6.QtCore import QByteArray, Signal, Slot
from PySide6.QtWidgets import QGroupBox
from PySide6.QtSerialBus import QCanBusFrame

from ui_sendframebox import Ui_SendFrameBox


THREE_HEX_DIGITS_PATTERN = re.compile("[0-9a-fA-F]{3}")
HEX_NUMBER_PATTERN = re.compile("^[0-9a-fA-F]+$")


MAX_STANDARD_ID = 0x7FF
MAX_EXTENDED_ID = 0x10000000
MAX_PAYLOAD = 8
MAX_PAYLOAD_FD = 64


def is_even_hex(input):
    return len(input.replace(" ", "")) % 2 == 0


def insert_space(string, pos):
    return string[0:pos] + " " + string[pos:]


# Formats a string of hex characters with a space between every byte
# Example: "012345" -> "01 23 45"
def format_hex_data(input):
    out = input.strip()
    while True:
        match = THREE_HEX_DIGITS_PATTERN.search(out)
        if match:
            out = insert_space(out, match.end(0) - 1)
        else:
            break
    return out.strip().upper()


class HexIntegerValidator(QValidator):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_maximum = MAX_STANDARD_ID

    def validate(self, input, pos):
        result = QValidator.Intermediate
        if input:
            result = QValidator.Invalid
            try:
                value = int(input, base=16)
                if value < self.m_maximum:
                    result = QValidator.Acceptable
            except ValueError:
                pass
        return result

    def set_maximum(self, maximum):
        self.m_maximum = maximum


class HexStringValidator(QValidator):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_maxLength = MAX_PAYLOAD

    def validate(self, input, pos):
        max_size = 2 * self.m_maxLength
        data = input.replace(" ", "")
        if not data:
            return QValidator.Intermediate

        # limit maximum size
        if len(data) > max_size:
            return QValidator.Invalid

        # check if all input is valid
        if not HEX_NUMBER_PATTERN.match(data):
            return QValidator.Invalid

        # insert a space after every two hex nibbles
        while True:
            match = THREE_HEX_DIGITS_PATTERN.search(input)
            if not match:
                break
            start = match.start(0)
            end = match.end()
            if pos == start + 1:
                # add one hex nibble before two - Abc
                input = insert_space(input, pos)
            elif pos == start + 2:
                # add hex nibble in the middle - aBc
                input = insert_space(input, end - 1)
                pos = end
            else:
                # add one hex nibble after two - abC
                input = insert_space(input, end - 1)
                pos = end + 1

        return (QValidator.Acceptable, input, pos)

    def set_max_length(self, maxLength):
        self.m_maxLength = maxLength


class SendFrameBox(QGroupBox):

    send_frame = Signal(QCanBusFrame)

    def __init__(self, parent):
        super().__init__(parent)
        self.m_ui = Ui_SendFrameBox()
        self.m_ui.setupUi(self)

        self.m_hexIntegerValidator = HexIntegerValidator(self)
        self.m_ui.frameIdEdit.setValidator(self.m_hexIntegerValidator)
        self.m_hexStringValidator = HexStringValidator(self)
        self.m_ui.payloadEdit.setValidator(self.m_hexStringValidator)

        self.m_ui.dataFrame.toggled.connect(self._data_frame)
        self.m_ui.remoteFrame.toggled.connect(self._remote_frame)
        self.m_ui.errorFrame.toggled.connect(self._error_frame)
        self.m_ui.extendedFormatBox.toggled.connect(self._extended_format)
        self.m_ui.flexibleDataRateBox.toggled.connect(self._flexible_datarate)
        self.m_ui.frameIdEdit.textChanged.connect(self._frameid_or_payload_changed)
        self.m_ui.payloadEdit.textChanged.connect(self._frameid_or_payload_changed)
        self._frameid_or_payload_changed()
        self.m_ui.sendButton.clicked.connect(self._send)

    @Slot(bool)
    def _data_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(True)

    @Slot(bool)
    def _remote_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(False)
            self.m_ui.flexibleDataRateBox.setChecked(False)

    @Slot(bool)
    def _error_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(False)
            self.m_ui.flexibleDataRateBox.setChecked(False)

    @Slot(bool)
    def _extended_format(self, value):
        m = MAX_EXTENDED_ID if value else MAX_STANDARD_ID
        self.m_hexIntegerValidator.set_maximum(m)

    @Slot(bool)
    def _flexible_datarate(self, value):
        len = MAX_PAYLOAD_FD if value else MAX_PAYLOAD
        self.m_hexStringValidator.set_max_length(len)
        self.m_ui.bitrateSwitchBox.setEnabled(value)
        if not value:
            self.m_ui.bitrateSwitchBox.setChecked(False)

    @Slot()
    def _frameid_or_payload_changed(self):
        has_frame_id = bool(self.m_ui.frameIdEdit.text())
        self.m_ui.sendButton.setEnabled(has_frame_id)
        tt = "" if has_frame_id else "Cannot send because no Frame ID was given."
        self.m_ui.sendButton.setToolTip(tt)
        if has_frame_id:
            is_even = is_even_hex(self.m_ui.payloadEdit.text())
            self.m_ui.sendButton.setEnabled(is_even)
            tt = "" if is_even else "Cannot send because Payload hex string is invalid."
            self.m_ui.sendButton.setToolTip(tt)

    @Slot()
    def _send(self):
        frame_id = int(self.m_ui.frameIdEdit.text(), base=16)
        data = self.m_ui.payloadEdit.text().replace(" ", "")
        self.m_ui.payloadEdit.setText(format_hex_data(data))
        payload = QByteArray.fromHex(bytes(data, encoding='utf8'))

        frame = QCanBusFrame(frame_id, payload)
        frame.setExtendedFrameFormat(self.m_ui.extendedFormatBox.isChecked())
        frame.setFlexibleDataRateFormat(self.m_ui.flexibleDataRateBox.isChecked())
        frame.setBitrateSwitch(self.m_ui.bitrateSwitchBox.isChecked())

        if self.m_ui.errorFrame.isChecked():
            frame.setFrameType(QCanBusFrame.ErrorFrame)
        elif self.m_ui.remoteFrame.isChecked():
            frame.setFrameType(QCanBusFrame.RemoteRequestFrame)

        self.send_frame.emit(frame)
