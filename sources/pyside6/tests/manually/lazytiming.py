# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
Time a repeated Python run
--------------------------

Usage: python3 lazytiming.py              # uses PySide6
       python3 lazytiming.py <any arg>    # uses PyQt6

It runs the same python for the testing.

Actually comparing PySide6 and PyQt6 in action:

    PYSIDE6_OPTION_LAZY=0 python3 sources/pyside6/tests/manually/lazytiming.py      # normal
    PYSIDE6_OPTION_LAZY=1 python3 sources/pyside6/tests/manually/lazytiming.py      # faster
                          python3 sources/pyside6/tests/manually/lazytiming.py xxx  # PyQt
"""
import subprocess
import sys

from timeit import default_timer as timer

repeats = 100
test1 = "PySide6"
test2 = "PyQt6"

test = test2 if sys.argv[1:] else test1
cmd = [sys.executable, "-c", f"from {test} import QtCore, QtGui, QtWidgets"]

print(f"{repeats} * {test}")

subprocess.call(cmd)        # warmup
start_time = timer()
for idx in range(repeats):
    subprocess.call(cmd)
stop_time = timer()
print(f"time per run = {(stop_time - start_time) / repeats}")
