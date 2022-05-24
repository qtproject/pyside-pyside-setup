# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from PySide6.QtWidgets import QApplication
from codeeditor import CodeEditor

"""PySide6 port of the widgets/codeeditor example from Qt5"""

if __name__ == "__main__":
    app = QApplication([])
    editor = CodeEditor()
    editor.setWindowTitle("Code Editor Example")
    editor.show()
    sys.exit(app.exec())
