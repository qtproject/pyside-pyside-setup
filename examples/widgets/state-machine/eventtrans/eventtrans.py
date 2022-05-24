# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QEvent, QRect, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtStateMachine import QEventTransition, QState, QStateMachine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        button = QPushButton(self)
        button.setGeometry(QRect(100, 100, 100, 100))

        machine = QStateMachine(self)
        s1 = QState()
        s1.assignProperty(button, 'text', 'Outside')
        s2 = QState()
        s2.assignProperty(button, 'text', 'Inside')

        enter_transition = QEventTransition(button, QEvent.Enter)
        enter_transition.setTargetState(s2)
        s1.addTransition(enter_transition)

        leave_transition = QEventTransition(button, QEvent.Leave)
        leave_transition.setTargetState(s1)
        s2.addTransition(leave_transition)

        s3 = QState()
        s3.assignProperty(button, 'text', 'Pressing...')

        press_transition = QEventTransition(button, QEvent.MouseButtonPress)
        press_transition.setTargetState(s3)
        s2.addTransition(press_transition)

        release_transition = QEventTransition(button, QEvent.MouseButtonRelease)
        release_transition.setTargetState(s2)
        s3.addTransition(release_transition)

        machine.addState(s1)
        machine.addState(s2)
        machine.addState(s3)

        machine.setInitialState(s1)
        machine.start()

        self.setCentralWidget(button)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    sys.exit(app.exec())
