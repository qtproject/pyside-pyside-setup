# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal


class Cart(QObject):
    # One notify signal per property, declared by hand.
    priceChanged = Signal()
    quantityChanged = Signal()
    totalChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._price = 10
        self._quantity = 2
        self._total = self._price * self._quantity

        # Keep the derived value in sync by hand
        # whenever an input changes, recompute the total.
        self.priceChanged.connect(self._recompute_total)
        self.quantityChanged.connect(self._recompute_total)

    # price: backing field + getter + setter, declared with @Property.
    @Property(int, notify=priceChanged)
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if self._price == value:
            return
        old = self._price
        self._price = value
        self.priceChanged.emit()
        # "watch" behaviour: react to the old and new values by hand.
        if value > old * 1.5:
            print(f"warning: price jumped {old} -> {value}")
        # "effect" behaviour: log the new state by hand.
        self._log_state()

    # quantity: the same boilerplate, a second time.
    @Property(int, notify=quantityChanged)
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if self._quantity == value:
            return
        self._quantity = value
        self.quantityChanged.emit()
        self._log_state()

    # total: read-only derived property, kept in sync manually. With no
    # setter it cannot be written from QML.
    @Property(int, notify=totalChanged)
    def total(self):
        return self._total

    def _recompute_total(self):
        new_total = self._price * self._quantity
        if new_total != self._total:
            self._total = new_total
            self.totalChanged.emit()

    def _log_state(self):
        print(f"cart: {self._price} x {self._quantity}")


if __name__ == "__main__":
    cart = Cart()
    print(f"initial total: {cart.total}")
    cart.price = 16      # 16 > 10 * 1.5, so the jump warning fires
    cart.quantity = 3
    print(f"final total: {cart.total}")
