# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Designer taskmenuextension example from Qt v6.x"""

import sys
from PySide6.QtWidgets import QApplication

from tictactoe import TicTacToe

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TicTacToe()
    window.state = "-X-XO----"
    window.show()
    sys.exit(app.exec())
