# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from __feature__ import snake_case  # noqa

"""
PYSIDE-3250: Tests that snake_case works when used in several files
"""

from PySide6.QtWidgets import QWidget  # noqa: E402


def test():
    print(__name__)
    widget = QWidget()
    return widget.size_hint()
