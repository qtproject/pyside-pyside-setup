# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQmlFeatures import auto_properties, computed, watch, effect, Change

# To be used on the @QmlElement decorator.
QML_IMPORT_NAME = "Shop"
QML_IMPORT_MAJOR_VERSION = 1


# Stack the decorators so @auto_properties runs first (innermost): it must
# add the generated Q_PROPERTYs to the QMetaObject before @QmlElement
# registers the type with the QML engine.
@QmlElement
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
    engine.addImportPath(sys.path[0])
    qml_file = Path(__file__).parent / "cart.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
