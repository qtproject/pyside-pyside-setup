# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""Test for pyside6-qml

The tests does a unittest and some integration tests for pyside6-qml."""

from asyncio.subprocess import PIPE
import os
import sys
import unittest
import subprocess
import importlib.util

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[2]))
from init_paths import init_test_paths
init_test_paths(False)


class TestPySide6QmlUnit(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._dir = Path(__file__).parent.resolve()
        self.pyside_root = self._dir.parents[4]

        self.pyqml_path = self.pyside_root / "sources" / "pyside-tools" / "qml.py"
        self.core_qml_path = (self.pyside_root / "examples" / "qml" /
                              "tutorials" / "extending-qml-advanced" / "adding")

        self.pyqml_run_cmd = [sys.executable, os.fspath(self.pyqml_path)]

        # self.pyqml_path will not abe able to find pyside and other related binaries, if not added
        # to path explicitly. The following lines does that.
        self.test_env = os.environ.copy()
        self.test_env["PYTHONPATH"] = os.pathsep + os.pathsep.join(sys.path)

    def testImportQmlModules(self):

        # because pyside-tools has a hyphen, a normal 'from pyside-tools import qml' cannot be done
        spec = importlib.util.spec_from_file_location("qml", self.pyqml_path)
        pyqml = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pyqml)
        pyqml.import_qml_modules(self.core_qml_path)

        # path added to sys.path
        self.assertIn(str(self.core_qml_path), sys.path)

        # module is imported
        self.assertIn("person", sys.modules.keys())

        # remove the imported modules
        sys.path.remove(str(self.core_qml_path))
        del sys.modules["person"]

        # test with module_paths - dir
        self.person_path = self.core_qml_path / "person.py"
        pyqml.import_qml_modules(self.core_qml_path, module_paths=[self.core_qml_path])
        self.assertIn(str(self.core_qml_path), sys.path)
        self.assertIn("person", sys.modules.keys())

        # test with module_paths - file - in testCoreApplication(self)

    def testCoreApplication(self):
        self.pyqml_run_cmd.extend(["--apptype", "core"])
        self.pyqml_run_cmd.append(str(self.core_qml_path / "People" / "Main.qml"))
        self.pyqml_run_cmd.extend(["-I", str(self.core_qml_path / "person.py")])

        result = subprocess.run(self.pyqml_run_cmd, stdout=PIPE, env=self.test_env)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.rstrip(), b"{'_name': 'Bob Jones', '_shoe_size': 12}")


if __name__ == '__main__':
    unittest.main()
