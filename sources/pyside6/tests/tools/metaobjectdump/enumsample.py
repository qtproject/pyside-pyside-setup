# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from enum import auto, IntEnum, IntFlag

from PySide6.QtCore import QEnum, QFlag, QObject
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Enums"
QML_IMPORT_MAJOR_VERSION = 1


class OuterIntEnum(IntEnum):
    OUTER_VALUE_0 = auto()
    OUTER_VALUE_1 = auto()


@QmlElement
class EnumSample(QObject):

    @QEnum
    class DecoratedIntEnum(IntEnum):
        VALUE_0 = auto()
        VALUE_1 = auto()

    class UndecoratedIntEnum(IntEnum):
        U_VALUE_0 = auto()
        U_VALUE_1 = auto()

    @QFlag
    class DecoratedIntFlag(IntFlag):
        FLAG_1 = 0x1
        FLAG_2 = 0x2
