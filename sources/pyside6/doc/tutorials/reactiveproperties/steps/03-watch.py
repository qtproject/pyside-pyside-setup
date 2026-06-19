# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtQmlFeatures import auto_properties, computed, watch, Change


@auto_properties
class Cart(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.price = 10
        self.quantity = 2

    @computed("price", "quantity")
    def total(self) -> int:
        return self.price * self.quantity

    # Runs after 'price' changes. The Change carries the old and new values,
    # so we can compare them. This replaces the by-hand tracking that lived
    # inside the manual setter.
    @watch("price")
    def on_price_changed(self, change: Change):
        if change.new > change.old * 1.5:
            print(f"warning: price jumped {change.old} -> {change.new}")


if __name__ == "__main__":
    cart = Cart()
    print(f"initial total: {cart.total}")
    cart.price = 16      # 16 > 10 * 1.5, so the @watch callback warns
    cart.quantity = 3
    print(f"final total: {cart.total}")
