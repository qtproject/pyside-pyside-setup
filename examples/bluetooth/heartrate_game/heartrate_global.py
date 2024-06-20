# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations
import os
import sys

_simulator = False


def simulator():
    global _simulator
    return _simulator


def set_simulator(s):
    global _simulator
    _simulator = s


is_android = os.environ.get('ANDROID_ARGUMENT')


def error_not_nuitka():
    """Errors and exits for macOS if run in interpreted mode.
    """
    is_nuitka = "__compiled__" in globals()
    if not is_nuitka and sys.platform == "darwin":
        print("This example does not work on macOS when Python is run in interpreted mode."
              "For this example to work on macOS, package the example using pyside6-deploy"
              "For more information, read `Notes for Developer` in the documentation")
        sys.exit(0)
