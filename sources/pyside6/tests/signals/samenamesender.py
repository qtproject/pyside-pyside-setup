# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from PySide6.QtCore import Signal, QObject


class SameNameSender(QObject):
    ''' Base class for the Test sender class of SameNameSenderTest (PYSIDE-3201).'''
    signal1 = Signal()
    signal2 = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
