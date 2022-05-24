#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout
from helper.usesqapplication import UsesQApplication


class QWidgetTest(UsesQApplication):

    def test_setLayout(self):
        layout = QVBoxLayout()
        btn1 = QPushButton("button_v1")
        layout.addWidget(btn1)

        btn2 = QPushButton("button_v2")
        layout.addWidget(btn2)

        layout2 = QHBoxLayout()

        btn1 = QPushButton("button_h1")
        layout2.addWidget(btn1)

        btn2 = QPushButton("button_h2")
        layout2.addWidget(btn2)

        layout.addLayout(layout2)

        widget = QWidget()
        widget.setLayout(layout)


if __name__ == '__main__':
    unittest.main()

