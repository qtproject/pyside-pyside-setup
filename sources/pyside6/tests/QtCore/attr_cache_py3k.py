# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

'''
Unit tests for attribute cache in Python 3

This is the original code from the bug report
https://bugreports.qt.io/browse/PYSIDE-60
'''

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QObject


class A(QObject):
    instance = 1

    @classmethod
    def test(cls):
        cls.instance
        cls.instance = cls()
        assert "<__main__.A(0x" in repr(cls.__dict__['instance'])
        assert "<__main__.A(0x" in repr(cls.instance)
        assert "<__main__.A(0x" in repr(type.__getattribute__(cls, 'instance'))


if __name__ == "__main__":
    A.test()
