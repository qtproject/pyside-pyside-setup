############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## BSD License Usage
## Alternatively, you may use this file under the terms of the BSD license
## as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
############################################################################

from tictactoe import TicTacToe

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtDesigner import (QExtensionFactory, QPyDesignerTaskMenuExtension)


class TicTacToeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._ticTacToe = TicTacToe(self)
        layout.addWidget(self._ticTacToe)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel
                                      | QDialogButtonBox.Reset)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        reset_button = button_box.button(QDialogButtonBox.Reset)
        reset_button.clicked.connect(self._ticTacToe.clear_board)
        layout.addWidget(button_box)

    def set_state(self, new_state):
        self._ticTacToe.setState(new_state)

    def state(self):
        return self._ticTacToe.state


class TicTacToeTaskMenu(QPyDesignerTaskMenuExtension):
    def __init__(self, ticTacToe, parent):
        super().__init__(parent)
        self._ticTacToe = ticTacToe
        self._edit_state_action = QAction('Edit State...', None)
        self._edit_state_action.triggered.connect(self._edit_state)

    def taskActions(self):
        return [self._edit_state_action]

    def preferredEditAction(self):
        return self._edit_state_action

    @Slot()
    def _edit_state(self):
        dialog = TicTacToeDialog(self._ticTacToe)
        dialog.set_state(self._ticTacToe.state)
        if dialog.exec() == QDialog.Accepted:
            self._ticTacToe.state = dialog.state()


class TicTacToeTaskMenuFactory(QExtensionFactory):
    def __init__(self, extension_manager):
        super().__init__(extension_manager)

    @staticmethod
    def task_menu_iid():
        return 'org.qt-project.Qt.Designer.TaskMenu'

    def createExtension(self, object, iid, parent):
        if iid != TicTacToeTaskMenuFactory.task_menu_iid():
            return None
        if object.__class__.__name__ != 'TicTacToe':
            return None
        return TicTacToeTaskMenu(object, parent)
