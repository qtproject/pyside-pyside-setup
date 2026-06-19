# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtQmlFeatures import auto_properties, computed


# @auto_properties turns the plain "self.price = ..." / "self.quantity = ..."
# assignments into real Q_PROPERTYs with priceChanged/quantityChanged notify
# signals, and turns the @computed method into a cached, read-only property.
@auto_properties
class Cart(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.price = 10
        self.quantity = 2

    # 'total' recomputes only when price or quantity changes. No backing
    # field, no notify signal, no manual recompute wiring.
    @computed("price", "quantity")
    def total(self) -> int:
        return self.price * self.quantity


if __name__ == "__main__":
    cart = Cart()
    print(f"initial total: {cart.total}")
    cart.price = 16
    cart.quantity = 3
    print(f"final total: {cart.total}")
