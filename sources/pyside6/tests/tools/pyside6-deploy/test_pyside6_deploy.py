# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import json
import unittest
import tempfile
import shutil
import sys
import os
import importlib
import platform
from pathlib import Path
from typing import Any
from unittest.mock import patch
from unittest import mock

sys.path.append(os.fspath(Path(__file__).resolve().parents[2]))
from init_paths import init_test_paths, _get_qt_lib_dir  # noqa: E402

init_test_paths(False)


def is_pyenv_python():
    pyenv_root = os.environ.get("PYENV_ROOT")
    if pyenv_root and (resolved_exe := str(Path(sys.executable).resolve())):
        return resolved_exe.startswith(pyenv_root)
    return False


class DeployTestBase(unittest.TestCase):
    @staticmethod
    def _sort_command(command: str) -> list[str]:
        """
        Given a command, returns a list obtained by text.split().
        Options starting with "--" are also sorted.
        """
        items = command.split()
        for idx in range(len(items)):
            if items[idx].startswith("--"):
                return items[:idx] + sorted(items[idx:])
        return items

    def assertCmdEqual(self, first: str, second: str, msg: Any = None):
        """
        Assert that two commands are equal. Sort their arguments
        """
        if not isinstance(first, str) or not isinstance(second, str):
            return super().assertEqual(first, second, msg)

        return super().assertEqual(self._sort_command(first), self._sort_command(second), msg)

    @classmethod
    def setUpClass(cls):
        cls.pyside_root = Path(__file__).parents[5].resolve()
        cls.example_root = cls.pyside_root / "examples"
        cls.temp_dir = tempfile.mkdtemp()
        cls.current_dir = Path.cwd()
        tools_path = cls.pyside_root / "sources" / "pyside-tools"
        cls.win_icon = tools_path / "deploy_lib" / "pyside_icon.ico"
        cls.linux_icon = tools_path / "deploy_lib" / "pyside_icon.jpg"
        cls.macos_icon = tools_path / "deploy_lib" / "pyside_icon.icns"
        if tools_path not in sys.path:
            sys.path.append(str(cls.pyside_root / "sources" / "pyside-tools"))
        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.deploy = importlib.import_module("deploy")
        cls.project_lib = importlib.import_module("project_lib")
        sys.modules["deploy"] = cls.deploy
        files_to_ignore = [".cpp.o", ".qsb"]
        cls.dlls_ignore_nuitka = " ".join([f"--noinclude-dlls=*{file}"
                                           for file in files_to_ignore])

        # required for comparing long strings
        cls.maxDiff = None

        # print no outputs to stdout
        sys.stdout = mock.MagicMock()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)


@unittest.skipIf(sys.platform == "darwin" and int(platform.mac_ver()[0].split('.')[0]) <= 11,
                 "Test only works on macOS version 12+")
@patch("deploy_lib.config.QtDependencyReader.find_plugin_dependencies")
class TestPySide6DeployWidgets(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_widgets = cls.example_root / "widgets" / "widgets" / "tetrix"
        cls.temp_example_widgets = Path(
            shutil.copytree(example_widgets, Path(cls.temp_dir) / "tetrix")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example_widgets)
        self.main_file = self.temp_example_widgets / "tetrix.py"
        self.deployment_files = self.temp_example_widgets / "deployment"
        # All the plugins included. This is different from plugins_nuitka, because Nuitka bundles
        # some plugins by default
        self.all_plugins = ["egldeviceintegrations", "generic", "iconengines",
                            "imageformats", "platforminputcontexts", "platforms",
                            "platformthemes", "styles", "xcbglintegrations"]
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = "platforminputcontexts"
        self.expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(self.main_file)} --follow-imports"
            f" --enable-plugin=pyside6 --output-dir={str(self.deployment_files)} --quiet"
            f" --noinclude-qt-translations"
            f" --include-qt-plugins={plugins_nuitka}"
            f" {self.dlls_ignore_nuitka}"
        )
        if sys.platform.startswith("linux"):
            self.expected_run_cmd += f" --linux-icon={str(self.linux_icon)} --onefile"
        elif sys.platform == "darwin":
            self.expected_run_cmd += (f" --macos-app-icon={str(self.macos_icon)}"
                                      " --macos-create-app-bundle --standalone")
        elif sys.platform == "win32":
            self.expected_run_cmd += f" --windows-icon-from-ico={str(self.win_icon)} --onefile"

        if is_pyenv_python():
            self.expected_run_cmd += " --static-libpython=no"
        self.config_file = self.temp_example_widgets / "pysidedeploy.spec"

    def testWidgetDryRun(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        # Checking for dry run commands is equivalent to mocking the subprocess.check_call()
        # in commands.py as the dry run command is the command being run.
        original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
        self.assertCmdEqual(original_output, self.expected_run_cmd)

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testWidgetConfigFile(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        mock_plugins.return_value = self.all_plugins
        # includes both dry run and config_file tests
        # init
        init_result = self.deploy.main(self.main_file, init=True, force=True)
        self.assertEqual(None, init_result)

        # test with config
        original_output = self.deploy.main(config_file=self.config_file, dry_run=True, force=True)
        self.assertCmdEqual(original_output, self.expected_run_cmd)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertTrue(config_obj.get_value("app", "input_file").endswith("tetrix.py"))
        self.assertTrue(config_obj.get_value("app", "project_dir").endswith("tetrix"))
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"),
                         "Nuitka==2.6.8")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), "")
        equ_base = "--quiet --noinclude-qt-translations"
        equ_value = equ_base + " --static-libpython=no" if is_pyenv_python() else equ_base
        self.assertEqual(config_obj.get_value("nuitka", "extra_args"), equ_value)
        self.assertEqual(config_obj.get_value("qt", "excluded_qml_plugins"), "")
        expected_modules = {"Core", "Gui", "Widgets"}
        if sys.platform != "win32":
            expected_modules.add("DBus")
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        obtained_qt_plugins = config_obj.get_value("qt", "plugins").split(",")
        self.assertEqual(obtained_qt_plugins.sort(), self.all_plugins.sort())
        self.config_file.unlink()

    def testErrorReturns(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        # Main file and config file do not exist
        fake_main_file = self.main_file.parent / "main.py"
        with self.assertRaises(RuntimeError) as context:
            self.deploy.main(main_file=fake_main_file, config_file=self.config_file)
        self.assertTrue("Directory does not contain main.py file." in str(context.exception))

    def testStandaloneMode(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        # Remove --onefile from self.expected_run_cmd and replace it with --standalone
        self.expected_run_cmd = self.expected_run_cmd.replace(" --onefile", " --standalone")
        # Test standalone mode
        original_output = self.deploy.main(self.main_file, mode="standalone", dry_run=True,
                                           force=True)

        self.assertCmdEqual(original_output, self.expected_run_cmd)

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testExtraModules(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        mock_plugins.return_value = self.all_plugins
        init_result = self.deploy.main(self.main_file, extra_modules_grouped="QtNetwork,QtOpenGL",
                                       init=True, force=True)
        self.assertEqual(None, init_result)
        self.deploy.main(config_file=self.config_file, dry_run=True, force=True)

        # Test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        expected_modules = {"Core", "Gui", "Widgets", "Network", "OpenGL"}
        if sys.platform != "win32":
            expected_modules.add("DBus")
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        self.config_file.unlink()

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testExtraIgnoreDirs(self, mock_sitepackages, mock_plugins):
        # Create a directory to ignore
        ignore_dir = self.temp_example_widgets / "ignore_dir"
        ignore_dir.mkdir()
        ignore_file = ignore_dir / "test_ignore.py"
        ignore_file.write_text("from PySide6 import QtNetwork")

        # rename the .pyproject file inside the example directory
        project_file = self.temp_example_widgets / "tetrix.pyproject"
        project_file.rename(self.temp_example_widgets / "tetrix.pyproject.bak")

        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        mock_plugins.return_value = self.all_plugins
        init_result = self.deploy.main(self.main_file, extra_ignore_dirs="ignore_dir",
                                       init=True, force=True)
        self.assertEqual(None, init_result)
        self.deploy.main(config_file=self.config_file, dry_run=True, force=True)

        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        expected_modules = {"Core", "Gui", "Widgets"}
        if sys.platform != "win32":
            expected_modules.add("DBus")
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        self.config_file.unlink()

        #undo rename of project file
        project_file = self.temp_example_widgets / "tetrix.pyproject.bak"
        project_file.rename(self.temp_example_widgets / "tetrix.pyproject")


@unittest.skipIf(sys.platform == "darwin" and int(platform.mac_ver()[0].split('.')[0]) <= 11,
                 "Test only works on macOS version 12+")
@patch("deploy_lib.config.QtDependencyReader.find_plugin_dependencies")
class TestPySide6DeployQml(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_qml = cls.example_root / "qml" / "editingmodel"
        cls.temp_example_qml = Path(
            shutil.copytree(example_qml, Path(cls.temp_dir) / "editingmodel")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example_qml)
        self.main_file = self.temp_example_qml / "main.py"
        self.deployment_files = self.temp_example_qml / "deployment"
        self.first_qml_file = "main.qml"
        self.second_qml_file = "MovingRectangle.qml"

        # All the plugins included. This is different from plugins_nuitka, because Nuitka bundles
        # some plugins by default
        self.all_plugins = ["egldeviceintegrations", "generic", "iconengines",
                            "imageformats", "networkinformation",
                            "platforminputcontexts", "platforms",
                            "platformthemes", "qmltooling", "tls",
                            "xcbglintegrations"]
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = "networkinformation,platforminputcontexts,qml,qmltooling"
        self.expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(self.main_file)} --follow-imports"
            f" --enable-plugin=pyside6 --output-dir={str(self.deployment_files)} --quiet"
            f" --noinclude-qt-translations"
            f" {self.dlls_ignore_nuitka}"
            " --noinclude-dlls=*/qml/QtQuickEffectMaker/*"
            f" --include-qt-plugins={plugins_nuitka}"
            f" --include-data-files={str(self.temp_example_qml / self.first_qml_file)}="
            f"./main.qml --include-data-files="
            f"{str(self.temp_example_qml / self.second_qml_file)}=./MovingRectangle.qml"
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
            self.expected_run_cmd += f" --linux-icon={str(self.linux_icon)} --onefile"
        elif sys.platform == "darwin":
            self.expected_run_cmd += (f" --macos-app-icon={str(self.macos_icon)}"
                                      " --macos-create-app-bundle --standalone")
        elif sys.platform == "win32":
            self.expected_run_cmd += f" --windows-icon-from-ico={str(self.win_icon)} --onefile"

        if is_pyenv_python():
            self.expected_run_cmd += " --static-libpython=no"
        self.config_file = self.temp_example_qml / "pysidedeploy.spec"

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testQmlConfigFile(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        mock_plugins.return_value = self.all_plugins
        # create config file
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            init_result = self.deploy.main(self.main_file, init=True, force=True)
            self.assertEqual(None, init_result)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertTrue(config_obj.get_value("app", "input_file").endswith("main.py"))
        self.assertTrue(config_obj.get_value("app", "project_dir").endswith("editingmodel"))
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"),
                         "Nuitka==2.6.8")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), "main.qml,MovingRectangle.qml")
        equ_base = "--quiet --noinclude-qt-translations"
        equ_value = equ_base + " --static-libpython=no" if is_pyenv_python() else equ_base
        self.assertEqual(config_obj.get_value("nuitka", "extra_args"), equ_value)
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest,QtWebEngine",
        )
        expected_modules = {"Core", "Gui", "Qml", "Quick", "Network", "OpenGL", "QmlModels",
                            "QmlWorkerScript", "QmlMeta"}

        # Exclude OpenGL if the platform is Windows and architecture is aarch64
        # https://bugreports.qt.io/browse/QTBUG-126030
        if sys.platform == "win32" and platform.machine() == "ARM64":
            expected_modules.remove("OpenGL")

        if sys.platform != "win32":
            expected_modules.add("DBus")
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        obtained_qt_plugins = config_obj.get_value("qt", "plugins").split(",")
        self.assertEqual(obtained_qt_plugins.sort(), self.all_plugins.sort())
        self.config_file.unlink()

    def testQmlDryRun(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
            self.assertCmdEqual(original_output, self.expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 1)

    def testMainFileDryRun(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            original_output = self.deploy.main(Path.cwd() / "main.py", dry_run=True, force=True)
            self.assertCmdEqual(original_output, self.expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 1)


@unittest.skipIf(sys.platform == "darwin" and int(platform.mac_ver()[0].split('.')[0]) <= 11,
                 "Test only works on macOS version 12+")
class TestPySide6DeployWebEngine(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_webenginequick = cls.example_root / "webenginequick" / "nanobrowser"
        cls.temp_example_webenginequick = Path(
            shutil.copytree(example_webenginequick, Path(cls.temp_dir) / "nanobrowser")
        ).resolve()

    @patch("deploy_lib.config.QtDependencyReader.find_plugin_dependencies")
    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testWebEngineQuickDryRun(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        all_plugins = ["egldeviceintegrations", "generic", "iconengines",
                       "imageformats", "networkinformation",
                       "platforminputcontexts", "platforms",
                       "platformthemes", "qmltooling", "tls",
                       "xcbglintegrations"]
        mock_plugins.return_value = all_plugins
        # this test case retains the QtWebEngine dlls
        # setup
        os.chdir(self.temp_example_webenginequick)
        main_file = self.temp_example_webenginequick / "quicknanobrowser.py"
        deployment_files = self.temp_example_webenginequick / "deployment"
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = "networkinformation,platforminputcontexts,qml,qmltooling"
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
                f"--include-data-files={str(self.temp_example_webenginequick / file)}=./{file}"
                for file in qml_files
            ]
        )
        expected_run_cmd = (
            f"{sys.executable} -m nuitka {str(main_file)} --follow-imports"
            f" --enable-plugin=pyside6 --output-dir={str(deployment_files)} --quiet"
            f" --noinclude-qt-translations --include-qt-plugins=all"
            f" {data_files_cmd}"
            f" --include-qt-plugins={plugins_nuitka}"
            f" {self.dlls_ignore_nuitka}"
            " --noinclude-dlls=*/qml/QtQuickEffectMaker/*"
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
            expected_run_cmd += f" --linux-icon={str(self.linux_icon)} --onefile"
        elif sys.platform == "darwin":
            expected_run_cmd += (f" --macos-app-icon={str(self.macos_icon)}"
                                 " --macos-create-app-bundle --standalone")
        elif sys.platform == "win32":
            expected_run_cmd += f" --windows-icon-from-ico={str(self.win_icon)} --onefile"

        config_file = self.temp_example_webenginequick / "pysidedeploy.spec"

        # create config file
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick", "QtWebEngine"]
            init_result = self.deploy.main(main_file, init=True, force=True)
            self.assertEqual(None, init_result)

            # run dry_run
            original_output = self.deploy.main(main_file, dry_run=True, force=True)
            self.assertTrue(original_output, expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 2)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=config_file)
        self.assertTrue(config_obj.get_value("app", "input_file").endswith("quicknanobrowser.py"))
        self.assertEqual(config_obj.get_value("qt", "qml_files"), ",".join(qml_files))
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest",
        )
        expected_modules = {"Core", "Gui", "Quick", "Qml", "WebEngineQuick", "Network", "OpenGL",
                            "QmlModels", "QmlWorkerScript", "QmlMeta", "WebEngineCore",
                            "Positioning", "WebChannelQuick", "WebChannel"}

        # Exclude specific modules if the platform is Windows and architecture is aarch64
        if sys.platform == "win32" and platform.machine() == "ARM64":
            excluded_modules = {"OpenGL", "WebEngineCore", "Positioning", "WebChannelQuick",
                                "WebChannel"}
            expected_modules.difference_update(excluded_modules)

        if sys.platform != "win32":
            expected_modules.add("DBus")

        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)


@unittest.skipIf(sys.platform != "win32", "Test only works on Windows")
class TestLongCommand(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_qml = cls.example_root / "qml" / "editingmodel"
        cls.temp_example_qml = Path(
            shutil.copytree(example_qml, Path(cls.temp_dir) / "editingmodel")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example_qml)
        self.main_file = self.temp_example_qml / "main.py"

    @patch('deploy_lib.nuitka_helper.os.remove')
    @patch("deploy_lib.config.run_qmlimportscanner")
    @patch('deploy.DesktopConfig.qml_files', new_callable=mock.PropertyMock)
    def test_main_with_mocked_qml_files(self, mock_qml_files, mock_qmlimportscanner, mock_remove):
        mock_qmlimportscanner.return_value = ["QtQuick"]
        mock_qml_files.return_value = [self.temp_example_qml / "MovingRectangle.qml"
                                       for _ in range(500)]

        command_str = self.deploy.main(self.main_file, force=True, keep_deployment_files=True,
                                       dry_run=True)
        mock_remove.assert_called_once()

        # check if command_str ends with deploy_main.py
        self.assertTrue(command_str.endswith("deploy_main.py"))

        # check if deploy_main.py starts with # nuitka-project:
        with open(self.temp_example_qml / "deploy_main.py", "r") as file:
            # check if 516 lines start with # nuitka-project:
            self.assertEqual(len([line for line in file.readlines()
                                  if line.startswith("# nuitka-project:")]), 516)


@unittest.skipIf(sys.platform == "darwin" and int(platform.mac_ver()[0].split('.')[0]) <= 11,
                 "Test only works on macOS version 12+")
@patch("deploy_lib.config.QtDependencyReader.find_plugin_dependencies")
class TestEmptyDSProject(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set up a Qt Design Studio empty Python project
        base_path = Path(cls.temp_dir) / "PythonProject"

        project_name = "TestProject"
        files = [
            base_path / "Python" / "autogen" / "settings.py",
            base_path / "Python" / "autogen" / "resources.py",
            base_path / "Python" / "main.py",
            base_path / project_name / "test.qml",
            base_path / f"{project_name}Content" / "test.qml",
            base_path / f"{project_name}.qmlproject",
            base_path / f"{project_name}.qmlproject.qtds",
            base_path / f"{project_name}.qrc"
        ]

        # Create the project files
        for file in files:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch(exist_ok=True)

        # Create a project file in the Python folder
        cls.pyproject_path = (base_path / "Python" / ".pyproject").resolve()
        cls.pyproject_path.touch()
        cls.pyproject_path.write_text(json.dumps({"files": ["main.py", "autogen/settings.py"]}))

        cls.temp_example = base_path

    def setUp(self):
        os.chdir(self.temp_example)
        self.temp_example = self.temp_example.resolve()
        self.main_file = self.temp_example / "Python" / "main.py"
        self.deployment_files = self.temp_example / "Python" / "deployment"

        self.expected_run_cmd = (
            f"{sys.executable} -m nuitka {self.main_file} --follow-imports"
            f" --enable-plugin=pyside6 --output-dir={self.deployment_files} --quiet"
            f" --noinclude-qt-translations"
            f" {self.dlls_ignore_nuitka}"
            f" --noinclude-dlls=*/qml/QtQuickEffectMaker/*"
            f" --include-qt-plugins=qml"
        )

        if sys.platform != "win32":
            self.expected_run_cmd += (
                " --noinclude-dlls=libQt6Charts* --noinclude-dlls=libQt6Quick*"
                " --noinclude-dlls=libQt6Quick3D* --noinclude-dlls=libQt6Sensors*"
                " --noinclude-dlls=libQt6Test* --noinclude-dlls=libQt6WebEngine*"
            )
        else:
            self.expected_run_cmd += (
                " --noinclude-dlls=Qt6Charts* --noinclude-dlls=Qt6Quick*"
                " --noinclude-dlls=Qt6Quick3D* --noinclude-dlls=Qt6Sensors*"
                " --noinclude-dlls=Qt6Test* --noinclude-dlls=Qt6WebEngine*"
            )

        if sys.platform.startswith("linux"):
            self.expected_run_cmd += f" --linux-icon={str(self.linux_icon)} --onefile"
        elif sys.platform == "darwin":
            self.expected_run_cmd += (f" --macos-app-icon={str(self.macos_icon)}"
                                      " --macos-create-app-bundle --standalone")
        elif sys.platform == "win32":
            self.expected_run_cmd += f" --windows-icon-from-ico={str(self.win_icon)} --onefile"

        if is_pyenv_python():
            self.expected_run_cmd += " --static-libpython=no"

        self.config_file = self.temp_example / "Python" / "pysidedeploy.spec"

    def testDryRun(self, mock_plugins):
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:  # noqa: F841
            original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
            self.assertCmdEqual(self.expected_run_cmd, original_output)

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testConfigFile(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:  # noqa: F841
            # Create the pysidedeploy.spec file only
            init_result = self.deploy.main(self.main_file, init=True, force=True)
            self.assertEqual(None, init_result)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)

        self.assertTrue(config_obj.get_value("app", "input_file").endswith("main.py"))
        self.assertTrue(config_obj.get_value("app", "project_dir").endswith("PythonProject"))

        expected_project_file = self.pyproject_path.relative_to(self.temp_example)
        self.assertEqual(str(expected_project_file), config_obj.get_value("app", "project_file"))

        self.config_file.unlink()


if __name__ == "__main__":
    unittest.main()
