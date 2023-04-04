# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import unittest
import tempfile
import shutil
import sys
import os
import importlib
from pathlib import Path
from configparser import ConfigParser
from unittest.mock import patch
from unittest import mock


class ConfigFile:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.parser = ConfigParser(comment_prefixes="/", allow_no_value=True)
        self.parser.read(self.config_file)

    def get_value(self, section: str, key: str):
        return str(self.parser.get(section, key))


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

        # required for comparing long strings
        cls.maxDiff = None

        # print no outputs to stdout
        sys.stdout = mock.MagicMock()

    def setUpWidgets(self):
        os.chdir(self.temp_example_widgets)
        self.main_file = self.temp_example_widgets / "tetrix.py"
        self.deployment_files = self.temp_example_widgets / "deployment"
        self.expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(self.main_file)} --follow-imports --onefile"
            f" --enable-plugin=pyside6 --output-dir={str(self.deployment_files)} --quiet"
            f" --noinclude-qt-translations=True"
        )
        if sys.platform.startswith("linux"):
            self.expected_run_cmd += f" --linux-onefile-icon={str(self.linux_onefile_icon)}"
        self.config_file = self.temp_example_widgets / "pysidedeploy.spec"

    def testWidgetDryRun(self):
        # Checking for dry run commands is equivalent to mocking the
        # subprocess.check_call() in commands.py as the the dry run command
        # is the command being run.
        self.setUpWidgets()
        original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
        self.assertEqual(original_output, self.expected_run_cmd)

    def testWidgetConfigFile(self):
        # includes both dry run and config_file tests

        self.setUpWidgets()
        # init
        init_result = self.deploy.main(self.main_file, init=True, force=True)
        self.assertEqual(init_result, None)

        # test with config
        original_output = self.deploy.main(config_file=self.config_file, dry_run=True, force=True)
        self.assertEqual(original_output, self.expected_run_cmd)

        # # test config file contents
        config_obj = ConfigFile(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "tetrix.py")
        self.assertEqual(config_obj.get_value("app", "project_dir"), ".")
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"), "nuitka==1.5.4,ordered_set,zstandard")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), "")
        self.assertEqual(
            config_obj.get_value("nuitka", "extra_args"), "--quiet --noinclude-qt-translations=True"
        )
        self.assertEqual(config_obj.get_value("qt", "excluded_qml_plugins"), "")
        self.config_file.unlink()

    def setUpQml(self):
        os.chdir(self.temp_example_qml)
        self.main_file = self.temp_example_qml / "main.py"
        self.deployment_files = self.temp_example_qml / "deployment"
        self.first_qml_file = "main.qml"
        self.second_qml_file = "MovingRectangle.qml"
        self.expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(self.main_file)} --follow-imports --onefile"
            f" --enable-plugin=pyside6 --output-dir={str(self.deployment_files)} --quiet"
            f" --noinclude-qt-translations=True --include-qt-plugins=all"
            f" --include-data-files={str(self.temp_example_qml / self.first_qml_file)}="
            f"./main.qml --include-data-files="
            f"{str(self.temp_example_qml /self.second_qml_file)}=./MovingRectangle.qml"
            )

        if sys.platform != "win32":
            self.expected_run_cmd += (
                " --noinclude-dlls=libQt6Charts*"
                " --noinclude-dlls=libQt6Quick3D* --noinclude-dlls=libQt6Sensors*"
                " --noinclude-dlls=libQt6Test* --noinclude-dlls=libQt6WebEngine*"
                )
        else:
            self.expected_run_cmd += (
                " --noinclude-dlls=Qt6Charts*"
                " --noinclude-dlls=Qt6Quick3D* --noinclude-dlls=Qt6Sensors*"
                " --noinclude-dlls=Qt6Test* --noinclude-dlls=Qt6WebEngine*"
                )

        if sys.platform.startswith("linux"):
            self.expected_run_cmd += f" --linux-onefile-icon={str(self.linux_onefile_icon)}"
        self.config_file = self.temp_example_qml / "pysidedeploy.spec"

    def testQmlConfigFile(self):
        self.setUpQml()

        # create config file
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            init_result = self.deploy.main(self.main_file, init=True, force=True)
            self.assertEqual(init_result, None)

        # test config file contents
        config_obj = ConfigFile(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "main.py")
        self.assertEqual(config_obj.get_value("app", "project_dir"), ".")
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"), "nuitka==1.5.4,ordered_set,zstandard")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), "main.qml,MovingRectangle.qml")
        self.assertEqual(
            config_obj.get_value("nuitka", "extra_args"), "--quiet --noinclude-qt-translations=True"
        )
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest,QtWebEngine",
        )
        self.config_file.unlink()

    def testQmlDryRun(self):
        self.setUpQml()
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
            self.assertEqual(original_output, self.expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 1)

    def testMainFileDryRun(self):
        self.setUpQml()
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            original_output = self.deploy.main(Path.cwd() / "main.py", dry_run=True, force=True)
            self.assertEqual(original_output, self.expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 1)

    # this test case retains the QtWebEngine dlls
    def testWebEngineQuickDryRun(self):
        # setup
        os.chdir(self.temp_example_webenginequick)
        main_file = self.temp_example_webenginequick / "quicknanobrowser.py"
        deployment_files = self.temp_example_webenginequick / "deployment"
        qml_files = [
            "ApplicationRoot.qml",
            "BrowserDialog.qml",
            "BrowserWindow.qml",
            "DownloadView.qml",
            "FindBar.qml",
            "FullScreenNotification.qml",
        ]
        data_files_cmd = " ".join(
            [
                f"--include-data-files={str(self.temp_example_webenginequick/file)}=./{file}"
                for file in qml_files
            ]
        )
        expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(main_file)} --follow-imports --onefile"
            f" --enable-plugin=pyside6 --output-dir={str(deployment_files)} --quiet"
            f" --noinclude-qt-translations=True --include-qt-plugins=all"
            f" {data_files_cmd}"
        )

        if sys.platform != "win32":
            expected_run_cmd += (
                " --noinclude-dlls=libQt6Charts*"
                " --noinclude-dlls=libQt6Quick3D* --noinclude-dlls=libQt6Sensors*"
                " --noinclude-dlls=libQt6Test*"
                )
        else:
            expected_run_cmd += (
                " --noinclude-dlls=Qt6Charts*"
                " --noinclude-dlls=Qt6Quick3D* --noinclude-dlls=Qt6Sensors*"
                " --noinclude-dlls=Qt6Test*"
                )

        if sys.platform.startswith("linux"):
            expected_run_cmd += f" --linux-onefile-icon={str(self.linux_onefile_icon)}"

        config_file = self.temp_example_webenginequick / "pysidedeploy.spec"

        # create config file
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick", "QtWebEngine"]
            init_result = self.deploy.main(main_file, init=True, force=True)
            self.assertEqual(init_result, None)

            # run dry_run
            original_output = self.deploy.main(main_file, dry_run=True, force=True)
            self.assertTrue(original_output, expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 2)

        # test config file contents
        config_obj = ConfigFile(config_file=config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "quicknanobrowser.py")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), ",".join(qml_files))
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest",
        )

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


if __name__ == "__main__":
    unittest.main()
