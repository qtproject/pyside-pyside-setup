# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from dialog import Dialog

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec())
