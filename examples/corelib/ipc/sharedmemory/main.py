# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the ipc/sharedmemory example from Qt v6.x"""

import sys
from PySide6.QtWidgets import QApplication
from dialog import Dialog


if __name__ == "__main__":
    application = QApplication()
    dialog = Dialog()
    dialog.show()
    sys.exit(application.exec())
