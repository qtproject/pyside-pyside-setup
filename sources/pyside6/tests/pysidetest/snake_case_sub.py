# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

"""
PYSIDE-2029: Tests that snake_case is isolated from imported modules
"""

from PySide6.QtWidgets import QWidget

def test_no_snake_case():
    print(__name__)
    widget = QWidget()
    check = widget.sizeHint
