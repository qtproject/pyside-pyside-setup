# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QTimer, Property, Slot
from PySide6.QtQml import QmlElement, QPyQmlPropertyValueSource

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "People"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class HappyBirthdaySong(QPyQmlPropertyValueSource):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_target = None
        self.m_name = ""
        self.m_line = -1
        self.m_lyrics = []

        self.m_timer = QTimer(self)
        self.m_timer.timeout.connect(self.advance)
        self.m_timer.start(1000)

    def setTarget(self, property):
        self.m_target = property

    @Property(str)
    def name(self):
        return self.m_name

    @name.setter
    def name(self, n):
        self.m_name = n
        self.m_lyrics = ["Happy birthday to you,",
                         "Happy birthday to you,",
                         f"Happy birthday dear {self.m_name},",
                         "Happy birthday to you!",
                         ""]

    @Slot()
    def advance(self):
        self.m_line = (self.m_line + 1) % len(self.m_lyrics)
        self.m_target.write(self.m_lyrics[self.m_line])
