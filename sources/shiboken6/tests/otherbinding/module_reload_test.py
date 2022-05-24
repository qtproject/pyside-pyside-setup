#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from importlib import reload
import os
import shutil
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()


orig_path = Path(__file__).parent
workdir = Path.cwd()
src = orig_path / 'test_module_template.py'
dst = workdir / 'test_module.py'
shutil.copyfile(src, dst)
sys.path.append(os.fspath(workdir))

class TestModuleReloading(unittest.TestCase):

    def testModuleReloading(self):
        '''Test module reloading with on-the-fly modifications.'''
        import test_module
        for i in range(3):
            oldObject = test_module.obj
            self.assertTrue(oldObject is test_module.obj)
            reload(test_module)
            self.assertFalse(oldObject is test_module.obj)

if __name__ == "__main__":
    unittest.main()
