# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Properties"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PropertySample(QObject):
    changed = Signal()

    @Property(str, constant=True)
    def constant_property(self) -> str:
        return ""

    @Property(int, notify=changed)
    def notifying_property(self) -> int:
        return 0
