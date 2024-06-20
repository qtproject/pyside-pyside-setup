# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Slot


class BitRateBox(QComboBox):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_isFlexibleDataRateEnabled = False
        self.m_customSpeedValidator = None
        self.m_customSpeedValidator = QIntValidator(0, 1000000, self)
        self.fill_bit_rates()
        self.currentIndexChanged.connect(self.check_custom_speed_policy)

    def bit_rate(self):
        index = self.currentIndex()
        if index == self.count() - 1:
            return int(self.currentText)
        return int(self.itemData(index))

    def is_flexible_data_rate_enabled(self):
        return self.m_isFlexibleDataRateEnabled

    def set_flexible_date_rate_enabled(self, enabled):
        self.m_isFlexibleDataRateEnabled = enabled
        self.m_customSpeedValidator.setTop(10000000 if enabled else 1000000)
        self.fill_bit_rates()

    @Slot(int)
    def check_custom_speed_policy(self, idx):
        is_custom_speed = not self.itemData(idx)
        self.setEditable(is_custom_speed)
        if is_custom_speed:
            self.clearEditText()
            self.lineEdit().setValidator(self.m_customSpeedValidator)

    def fill_bit_rates(self):
        rates = [10000, 20000, 50000, 100000, 125000, 250000, 500000,
                 800000, 1000000]
        data_rates = [2000000, 4000000, 8000000]

        self.clear()
        for rate in rates:
            self.addItem(f"{rate}", rate)

        if self.is_flexible_data_rate_enabled():
            for rate in data_rates:
                self.addItem(f"{rate}", rate)

        self.addItem("Custom")
        self.setCurrentIndex(6)  # default is 500000 bits/sec
