# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox

from ui_canbusdeviceinfobox import Ui_CanBusDeviceInfoBox


def _set_readonly_and_compact(box):
    box.setAttribute(Qt.WA_TransparentForMouseEvents)
    box.setFocusPolicy(Qt.NoFocus)
    box.setStyleSheet("margin-top:0; margin-bottom:0;")


class CanBusDeviceInfoBox(QGroupBox):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_ui = Ui_CanBusDeviceInfoBox()
        self.m_ui.setupUi(self)
        _set_readonly_and_compact(self.m_ui.isVirtual)
        _set_readonly_and_compact(self.m_ui.isFlexibleDataRateCapable)

    def clear(self):
        self.m_ui.pluginLabel.clear()
        self.m_ui.nameLabel.clear()
        self.m_ui.descriptionLabel.clear()
        self.m_ui.serialNumberLabel.clear()
        self.m_ui.aliasLabel.clear()
        self.m_ui.channelLabel.clear()
        self.m_ui.isVirtual.setChecked(False)
        self.m_ui.isFlexibleDataRateCapable.setChecked(False)

    def set_device_info(self, info):
        self.m_ui.pluginLabel.setText(f"Plugin: {info.plugin()}")
        self.m_ui.nameLabel.setText(f"Name: {info.name()}")
        self.m_ui.descriptionLabel.setText(info.description())
        serial_number = info.serialNumber()
        if not serial_number:
            serial_number = "n/a"
        self.m_ui.serialNumberLabel.setText(f"Serial: {serial_number}")
        alias = info.alias()
        if not alias:
            alias = "n/a"
        self.m_ui.aliasLabel.setText(f"Alias: {alias}")
        self.m_ui.channelLabel.setText(f"Channel: {info.channel()}")
        self.m_ui.isVirtual.setChecked(info.isVirtual())
        self.m_ui.isFlexibleDataRateCapable.setChecked(info.hasFlexibleDataRate())
