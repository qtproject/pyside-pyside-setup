# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QDialog

from ui_canbusdeviceinfodialog import Ui_CanBusDeviceInfoDialog


class CanBusDeviceInfoDialog(QDialog):

    def __init__(self, info, parent):
        super().__init__(parent)
        self.m_ui = Ui_CanBusDeviceInfoDialog()
        self.m_ui.setupUi(self)
        self.m_ui.deviceInfoBox.set_device_info(info)
        self.m_ui.okButton.pressed.connect(self.close)
