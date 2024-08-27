# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import unittest
import tempfile
import shutil
import sys
import os
import importlib
import platform
from pathlib import Path
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


class LongSortedOptionTest(unittest.TestCase):
    @staticmethod
    def _option_prepare(s):
        """
        Take a string and return a list obtained by text.split().
        Options starting with "--" are also sorted."
        """
        items = s.split()
        for idx in range(len(items)):
            if items[idx].startswith("--"):
                return items[:idx] + sorted(items[idx:])
        return items

    def assertEqual(self, text_a, text_b):
        if (not isinstance(text_a, str) or not isinstance(text_b, str)
                or (len(text_a) < 50 and len(text_b) < 50)):
            return super().assertEqual(text_a, text_b)
        sort_a = self._option_prepare(text_a)
        sort_b = self._option_prepare(text_b)
        return super().assertEqual(sort_a, sort_b)


class DeployTestBase(LongSortedOptionTest):
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
        sys.modules["deploy"] = cls.deploy
        files_to_ignore = [".cpp.o", ".qsb", ".webp"]
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
        self.all_plugins = ["accessiblebridge", "egldeviceintegrations", "generic", "iconengines",
                            "imageformats", "platforminputcontexts", "platforms",
                            "platforms/darwin", "platformthemes", "styles", "xcbglintegrations"]
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = ("accessiblebridge,platforminputcontexts,platforms/darwin")
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
        # Checking for dry run commands is equivalent to mocking the
        # subprocess.check_call() in commands.py as the the dry run command
        # is the command being run.
        original_output = self.deploy.main(self.main_file, dry_run=True, force=True)
        self.assertEqual(original_output, self.expected_run_cmd)

    @patch("deploy_lib.dependency_util.QtDependencyReader.get_qt_libs_dir")
    def testWidgetConfigFile(self, mock_sitepackages, mock_plugins):
        mock_sitepackages.return_value = Path(_get_qt_lib_dir())
        mock_plugins.return_value = self.all_plugins
        # includes both dry run and config_file tests
        # init
        init_result = self.deploy.main(self.main_file, init=True, force=True)
        self.assertEqual(init_result, None)

        # test with config
        original_output = self.deploy.main(config_file=self.config_file, dry_run=True, force=True)
        self.assertEqual(original_output, self.expected_run_cmd)

        # # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "tetrix.py")
        self.assertEqual(config_obj.get_value("app", "project_dir"), ".")
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"),
                         "Nuitka==2.4.8")
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
        # main file and config file does not exists
        fake_main_file = self.main_file.parent / "main.py"
        with self.assertRaises(RuntimeError) as context:
            self.deploy.main(main_file=fake_main_file, config_file=self.config_file)
        self.assertTrue("Directory does not contain main.py file." in str(context.exception))

    def testStandaloneMode(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        # remove --onefile from self.expected_run_cmd and replace it with --standalone
        self.expected_run_cmd = self.expected_run_cmd.replace(" --onefile", " --standalone")
        # test standalone mode
        original_output = self.deploy.main(self.main_file, mode="standalone", dry_run=True,
                                           force=True)

        self.assertEqual(original_output, self.expected_run_cmd)


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
        self.all_plugins = ["accessiblebridge", "egldeviceintegrations", "generic", "iconengines",
                            "imageformats", "networkaccess", "networkinformation",
                            "platforminputcontexts", "platforms", "platforms/darwin",
                            "platformthemes", "qmltooling", "scenegraph", "tls",
                            "xcbglintegrations"]
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = ("accessiblebridge,networkaccess,networkinformation,platforminputcontexts,"
                          "platforms/darwin,qml,qmltooling,scenegraph")
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
            self.assertEqual(init_result, None)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "main.py")
        self.assertEqual(config_obj.get_value("app", "project_dir"), ".")
        self.assertEqual(config_obj.get_value("app", "exec_directory"), ".")
        self.assertEqual(config_obj.get_value("python", "packages"),
                         "Nuitka==2.4.8")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), "main.qml,MovingRectangle.qml")
        equ_base = "--quiet --noinclude-qt-translations"
        equ_value = equ_base + " --static-libpython=no" if is_pyenv_python() else equ_base
        self.assertEqual(config_obj.get_value("nuitka", "extra_args"), equ_value)
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest,QtWebEngine",
        )
        expected_modules = {"Core", "Gui", "Qml", "Quick", "Network", "OpenGL", "QmlModels"}
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
            self.assertEqual(original_output, self.expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 1)

    def testMainFileDryRun(self, mock_plugins):
        mock_plugins.return_value = self.all_plugins
        with patch("deploy_lib.config.run_qmlimportscanner") as mock_qmlimportscanner:
            mock_qmlimportscanner.return_value = ["QtQuick"]
            original_output = self.deploy.main(Path.cwd() / "main.py", dry_run=True, force=True)
            self.assertEqual(original_output, self.expected_run_cmd)
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
        all_plugins = ["accessiblebridge", "egldeviceintegrations", "generic", "iconengines",
                       "imageformats", "networkaccess", "networkinformation",
                       "platforminputcontexts", "platforms", "platforms/darwin",
                       "platformthemes", "qmltooling", "scenegraph", "tls",
                       "xcbglintegrations"]
        mock_plugins.return_value = all_plugins
        # this test case retains the QtWebEngine dlls
        # setup
        os.chdir(self.temp_example_webenginequick)
        main_file = self.temp_example_webenginequick / "quicknanobrowser.py"
        deployment_files = self.temp_example_webenginequick / "deployment"
        # Plugins that needs to be passed to Nuitka
        plugins_nuitka = ("accessiblebridge,networkaccess,networkinformation,platforminputcontexts,"
                          "platforms/darwin,qml,qmltooling,scenegraph")
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
            self.assertEqual(init_result, None)

            # run dry_run
            original_output = self.deploy.main(main_file, dry_run=True, force=True)
            self.assertTrue(original_output, expected_run_cmd)
            self.assertEqual(mock_qmlimportscanner.call_count, 2)

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "quicknanobrowser.py")
        self.assertEqual(config_obj.get_value("qt", "qml_files"), ",".join(qml_files))
        self.assertEqual(
            config_obj.get_value("qt", "excluded_qml_plugins"),
            "QtCharts,QtQuick3D,QtSensors,QtTest",
        )
        expected_modules = {"Core", "Gui", "Quick", "Qml", "WebEngineQuick", "Network", "OpenGL",
                            "Positioning", "WebEngineCore", "WebChannel", "WebChannelQuick",
                            "QmlModels"}
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

        # check if deploy_main.py startes with # nuitka-project:
        with open(self.temp_example_qml / "deploy_main.py", "r") as file:
            # check if 517 lines start with # nuitka-project:
            self.assertEqual(len([line for line in file.readlines()
                                  if line.startswith("# nuitka-project:")]), 517)


if __name__ == "__main__":
    unittest.main()
