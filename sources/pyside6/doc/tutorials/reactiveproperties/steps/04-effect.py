# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtQmlFeatures import auto_properties, computed, watch, effect, Change


@auto_properties
class Cart(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.price = 10
        self.quantity = 2

    @computed("price", "quantity")
    def total(self) -> int:
        return self.price * self.quantity

    @watch("price")
    def on_price_changed(self, change: Change):
        if change.new > change.old * 1.5:
            print(f"warning: price jumped {change.old} -> {change.new}")

    # Runs after price or quantity changes. Unlike @watch it gets no Change;
    # it just reacts to the new state. This replaces the _log_state() calls
    # that the manual setters had to make by hand.
    @effect("price", "quantity")
    def log_state(self):
        print(f"cart: {self.price} x {self.quantity}")


if __name__ == "__main__":
    cart = Cart()
    print(f"initial total: {cart.total}")
    cart.price = 16
    cart.quantity = 3
    print(f"final total: {cart.total}")
