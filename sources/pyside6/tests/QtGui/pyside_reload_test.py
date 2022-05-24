# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import importlib
import importlib.util
import os
import shutil
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)


orig_path = os.path.join(os.path.dirname(__file__))
workdir = os.getcwd()
src = os.path.normpath(os.path.join(orig_path, '..', 'QtWidgets', 'test_module_template.py'))
dst = os.path.join(workdir, 'test_module.py')
shutil.copyfile(src, dst)
sys.path.append(workdir)


def reload_module(moduleName):
    importlib.reload(moduleName)


def increment_module_value():
    modfile = open(dst, 'a')
    modfile.write('Sentinel.value += 1' + os.linesep)
    modfile.flush()
    modfile.close()
    if not sys.dont_write_bytecode:
        import importlib.util
        cacheFile = importlib.util.cache_from_source(dst)
        os.remove(cacheFile)


class TestModuleReloading(unittest.TestCase):

    def testModuleReloading(self):
        '''Test module reloading with on-the-fly modifications.'''

        import test_module
        self.assertEqual(test_module.Sentinel.value, 10)

        increment_module_value()
        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 11)

        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 11)

        increment_module_value()
        reload_module(sys.modules['test_module'])
        self.assertEqual(test_module.Sentinel.value, 12)


if __name__ == "__main__":
    unittest.main()


