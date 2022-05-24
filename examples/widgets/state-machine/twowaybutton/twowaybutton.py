# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtStateMachine import QState, QStateMachine


if __name__ == '__main__':
    app = QApplication(sys.argv)
    button = QPushButton()
    machine = QStateMachine()

    off = QState()
    off.assignProperty(button, 'text', 'Off')
    off.setObjectName('off')

    on = QState()
    on.setObjectName('on')
    on.assignProperty(button, 'text', 'On')

    off.addTransition(button.clicked, on)
    on.addTransition(button.clicked, off)

    machine.addState(off)
    machine.addState(on)
    machine.setInitialState(off)
    machine.start()
    button.resize(100, 50)
    button.show()
    sys.exit(app.exec())
