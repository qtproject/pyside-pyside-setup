# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys


_simulator = sys.platform == "win32"


def simulator():
    global _simulator
    return _simulator


def set_simulator(s):
    global _simulator
    _simulator = s
