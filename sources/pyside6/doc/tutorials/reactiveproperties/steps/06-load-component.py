# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQmlFeatures import (auto_properties, computed, watch, effect,
                                   Change, load_qml_component)


# The reactive model is unchanged from Step 4: no @QmlElement this time,
# because the model stays in Python and QML never instantiates it.
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

    @effect("price", "quantity")
    def log_state(self):
        print(f"cart: {self.price} x {self.quantity}")


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # This time the reactive model lives in Python, not in QML.
    cart = Cart()

    # Pull the QML view into Python with load_qml_component() and create an
    # instance. 'view' is a Pythonic wrapper whose QML properties are plain
    # attributes, so we can assign to view.total, view.price, etc.
    view_factory = load_qml_component(engine, "cartview.qml")
    view = view_factory.create()

    # Push the reactive values into the loaded QML view. Connecting to the
    # input notify signals is enough: reading cart.total recomputes the
    # @computed value on demand.
    def sync():
        view.price = cart.price
        view.quantity = cart.quantity
        view.total = cart.total

    cart.priceChanged.connect(sync)
    cart.quantityChanged.connect(sync)
    sync()

    # Drive the reactive model from Python. Each assignment runs the @watch
    # and @effect callbacks (console output) and, through sync(), updates the
    # QML view that was loaded from Python.
    def tick():
        cart.price += 2
        if cart.price > 30:
            cart.price = 10
            cart.quantity = cart.quantity % 5 + 1

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(500)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
