# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from tictactoe import TicTacToe
from tictactoetaskmenu import TicTacToeTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface


DOM_XML = """
<ui language='c++'>
    <widget class='TicTacToe' name='ticTacToe'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>200</width>
                <height>200</height>
            </rect>
        </property>
        <property name='state'>
            <string>-X-XO----</string>
        </property>
    </widget>
</ui>
"""


class TicTacToePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        t = TicTacToe(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'tictactoe'

    def initialize(self, form_editor):
        self._form_editor = form_editor
        manager = form_editor.extensionManager()
        iid = TicTacToeTaskMenuFactory.task_menu_iid()
        manager.registerExtensions(TicTacToeTaskMenuFactory(manager), iid)

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return 'TicTacToe'

    def toolTip(self):
        return 'Tic Tac Toe Example, demonstrating class QDesignerTaskMenuExtension (Python)'

    def whatsThis(self):
        return self.toolTip()
