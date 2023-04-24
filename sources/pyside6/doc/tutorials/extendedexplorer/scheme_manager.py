# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import json
from pathlib import Path
from PySide6.QtCore import Slot, QObject, Property, Signal
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlNamedElement, QmlSingleton

QML_IMPORT_NAME = "FileSystemModule"
QML_IMPORT_MAJOR_VERSION = 1


@QmlNamedElement("Colors")
@QmlSingleton
class SchemeManager(QObject):

    schemeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        with open(Path(__file__).parent / "schemes.json", 'r') as f:
            self.m_schemes = json.load(f)
        self.m_activeScheme = {}
        self.m_activeSchemeName = "Catppuccin"
        self.setScheme(self.m_activeSchemeName)

    @Slot(str)
    def setScheme(self, theme):
        for k, v in self.m_schemes[theme].items():
            self.m_activeScheme[k] = QColor.fromString(v)
        self.m_activeSchemeName = theme
        self.schemeChanged.emit()

    @Slot(result='QStringList')
    def getKeys(self):
        return self.m_schemes.keys()

    @Property('QStringList', notify=schemeChanged)
    def currentColors(self):
        return self.m_schemes[self.m_activeSchemeName].values()

    @Property(QColor, notify=schemeChanged)
    def background(self):
        return self.m_activeScheme["background"]

    @Property(QColor, notify=schemeChanged)
    def surface1(self):
        return self.m_activeScheme["surface1"]

    @Property(QColor, notify=schemeChanged)
    def surface2(self):
        return self.m_activeScheme["surface2"]

    @Property(QColor, notify=schemeChanged)
    def text(self):
        return self.m_activeScheme["text"]

    @Property(QColor, notify=schemeChanged)
    def textFile(self):
        return self.m_activeScheme["textFile"]

    @Property(QColor, notify=schemeChanged)
    def disabledText(self):
        return self.m_activeScheme["disabledText"]

    @Property(QColor, notify=schemeChanged)
    def selection(self):
        return self.m_activeScheme["selection"]

    @Property(QColor, notify=schemeChanged)
    def active(self):
        return self.m_activeScheme["active"]

    @Property(QColor, notify=schemeChanged)
    def inactive(self):
        return self.m_activeScheme["inactive"]

    @Property(QColor, notify=schemeChanged)
    def folder(self):
        return self.m_activeScheme["folder"]

    @Property(QColor, notify=schemeChanged)
    def icon(self):
        return self.m_activeScheme["icon"]

    @Property(QColor, notify=schemeChanged)
    def iconIndicator(self):
        return self.m_activeScheme["iconIndicator"]

    @Property(QColor, notify=schemeChanged)
    def color1(self):
        return self.m_activeScheme["color1"]

    @Property(QColor, notify=schemeChanged)
    def color2(self):
        return self.m_activeScheme["color2"]
