# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# trimmed down diagramscene.py to demonstrate crash in sizeHint()

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QGraphicsProxyWidget


class CustomWidget(QGraphicsProxyWidget):
    def itemChange(self, eventType, value):
        QGraphicsProxyWidget.itemChange(self, eventType, value)


class Bug589(unittest.TestCase):
    def testCase(self):
        widget = QGraphicsProxyWidget()
        custom = CustomWidget()
        custom.setParentItem(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
