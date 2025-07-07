# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import unittest

from tempfile import TemporaryDirectory
from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)


def reload_module(moduleName):
    importlib.reload(moduleName)


class TestModuleReloading(unittest.TestCase):
    def setUp(self):
        orig_path = Path(__file__).resolve().parent
        self._src = orig_path / 'test_module_template.py'
        self._workdir = TemporaryDirectory()
        self._dst = Path(self._workdir.name) / 'test_module.py'
        self._dst.write_bytes(self._src.read_bytes())
        sys.path.append(self._workdir.name)

    def tearDown(self):
        sys.path.remove(self._workdir.name)
        self._workdir = None

    def _increment_module_value(self):
        with self._dst.open(mode='a') as modfile:
            modfile.write('Sentinel.value += 1\n')
        if not sys.dont_write_bytecode:
            import importlib.util
            cacheFile = importlib.util.cache_from_source(os.fspath(self._dst))
            os.remove(cacheFile)

    def testModuleReloading(self):
        '''Test module reloading with on-the-fly modifications.'''

        import test_module
        self.assertEqual(test_module.Sentinel.value, 10)

        self._increment_module_value()
        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 11)

        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 11)

        self._increment_module_value()
        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 12)


if __name__ == "__main__":
    unittest.main()
