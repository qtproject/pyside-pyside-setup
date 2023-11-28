# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
    Extensive manual test of pyside6-deploy

    Note: Not to be added into the CI
"""

import logging
import unittest
import tempfile
import shutil
import sys
import os
import importlib
from pathlib import Path


class TestPySide6Deploy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyside_root = Path(__file__).parents[5].resolve()
        example_root = cls.pyside_root / "examples"
        example_widgets = example_root / "widgets" / "widgets" / "tetrix"
        example_qml = example_root / "qml" / "editingmodel"
        example_webenginequick = example_root / "webenginequick" / "nanobrowser"
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_example_widgets = Path(
            shutil.copytree(example_widgets, Path(cls.temp_dir) / "tetrix")
        ).resolve()
        cls.temp_example_qml = Path(
            shutil.copytree(example_qml, Path(cls.temp_dir) / "editingmodel")
        ).resolve()
        cls.temp_example_webenginequick = Path(
            shutil.copytree(example_webenginequick, Path(cls.temp_dir) / "nanobrowser")
        ).resolve()
        cls.current_dir = Path.cwd()
        cls.linux_onefile_icon = (
            cls.pyside_root / "sources" / "pyside-tools" / "deploy_lib" / "pyside_icon.jpg"
        )

        sys.path.append(str(cls.pyside_root / "sources" / "pyside-tools"))
        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.deploy = importlib.import_module("deploy")
        sys.modules["deploy"] = cls.deploy

    def setUpWidgets(self):
        os.chdir(self.temp_example_widgets)
        self.main_file = self.temp_example_widgets / "tetrix.py"
        self.config_file = self.temp_example_widgets / "pysidedeploy.spec"

    def testWidget(self):
        self.setUpWidgets()
        self.deploy.main(self.main_file, name="widget_app", loglevel=logging.INFO,
                         keep_deployment_files=True, force=True)

        print("Now testing Widget with config file")
        self.deploy.main(self.main_file, config_file=self.config_file, loglevel=logging.INFO,
                         force=True)

    def setUpQml(self):
        os.chdir(self.temp_example_qml)
        self.main_file = self.temp_example_qml / "main.py"
        self.config_file = self.temp_example_qml / "pysidedeploy.spec"

    def testQml(self):
        self.setUpQml()
        self.deploy.main(self.main_file, name="qml_app", loglevel=logging.INFO,
                         keep_deployment_files=True, force=True)

    def testWebEngineQuickDryRun(self):
        os.chdir(self.temp_example_webenginequick)
        main_file = self.temp_example_webenginequick / "quicknanobrowser.py"
        self.deploy.main(main_file, name="qml_app", keep_deployment_files=True,
                         loglevel=logging.INFO, force=True)

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


if __name__ == "__main__":
    unittest.main()
