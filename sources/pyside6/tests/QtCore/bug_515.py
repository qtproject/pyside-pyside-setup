# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

""" Unittest for bug #515 """
""" http://bugs.openbossa.org/show_bug.cgi?id=515 """

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QCoreApplication, qAddPostRoutine


callCleanup = False


def _cleanup():
    global callCleanup
    callCleanup = True


def _checkCleanup():
    global callCleanup
    assert(callCleanup)


app = QCoreApplication([])
qAddPostRoutine(_cleanup)
qAddPostRoutine(_checkCleanup)
del app
