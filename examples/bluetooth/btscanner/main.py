# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the bluetooth/btscanner example from Qt v6.x"""

import sys

from PySide6.QtWidgets import QApplication

from device import DeviceDiscoveryDialog


if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = DeviceDiscoveryDialog()
    d.exec()
    sys.exit(0)
