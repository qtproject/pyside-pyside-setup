#!/usr/bin/python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''An enum at module scope is an IntEnum, whatever enum was created before it.'''

import enum
import importlib
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6


def module_scope_enums(module):
    """The enums defined at the top level of a module."""
    return [obj for obj in vars(module).values()
            if isinstance(obj, enum.EnumMeta) and obj.__module__ == module.__name__
            and "." not in obj.__qualname__]


class ModuleScopeEnumTest(unittest.TestCase):
    def testQtCoreEnums(self):
        from PySide6 import QtCore
        for name in ("QtMsgType", "QCborKnownTags", "QCborSimpleType", "QCborTag"):
            with self.subTest(name=name):
                self.assertTrue(issubclass(getattr(QtCore, name), enum.IntEnum))

    def testAllModules(self):
        # The base used to be the one of the last enum created in a class
        checked = 0
        for short in sorted(PySide6.__all__):
            module = importlib.import_module(f"PySide6.{short}")
            for enum_type in module_scope_enums(module):
                with self.subTest(enum=f"{short}.{enum_type.__qualname__}"):
                    self.assertTrue(issubclass(enum_type, enum.IntEnum))
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == '__main__':
    unittest.main()
