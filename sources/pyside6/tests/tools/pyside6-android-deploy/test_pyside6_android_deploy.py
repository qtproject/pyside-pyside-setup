# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import importlib
import os
import re
import shutil
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest import mock
from unittest.mock import patch

sys.path.append(os.fspath(Path(__file__).resolve().parents[2]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)


class DeployTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyside_root = Path(__file__).parents[5].resolve()
        cls.example_root = cls.pyside_root / "examples"
        cls.temp_dir = tempfile.mkdtemp()
        cls.current_dir = Path.cwd()
        cls.pyside_wheel = Path("/tmp/PySide6-6.5.0a1-6.5.0-cp37-abi3-android_x86_64.whl")
        cls.shiboken_wheel = Path("/tmp/shiboken6-6.5.0a1-6.5.0-cp37-abi3-android_x86_64.whl")
        cls.ndk_path = Path("/tmp/android_sdk/ndk/25.2.9519653")
        cls.sdk_path = Path("/tmp/android_sdk")
        pyside_tools = cls.pyside_root / "sources" / "pyside-tools"

        # install extra python dependencies
        android_requirements_file = pyside_tools / "requirements-android.txt"
        with open(android_requirements_file, 'r', encoding='UTF-8') as file:
            while line := file.readline():
                dependent_package = line.rstrip()
                if not bool(importlib.util.find_spec(dependent_package)):
                    command = [sys.executable, "-m", "pip", "install", dependent_package]
                    subprocess.run(command)

        sys.path.append(str(pyside_tools))
        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.android_deploy = importlib.import_module("android_deploy")
        sys.modules["android_deploy"] = cls.android_deploy

        # required for comparing long strings
        cls.maxDiff = None

        # print no outputs to stdout
        sys.stdout = mock.MagicMock()

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


@patch("deploy_lib.android.android_config.extract_and_copy_jar")
class TestPySide6AndroidDeployWidgets(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_widget_application = cls.example_root / "gui" / "analogclock"
        cls.temp_example = Path(
            shutil.copytree(example_widget_application, Path(cls.temp_dir) / "analogclock")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example)
        self.config_file = self.temp_example / "pysidedeploy.spec"
        self.buildozer_config = self.temp_example / "buildozer.spec"

    @patch("deploy_lib.android.android_config.AndroidConfig._find_local_libs")
    @patch("deploy_lib.android.android_config.AndroidConfig._find_dependent_qt_modules")
    @patch("deploy_lib.android.android_config.find_qtlibs_in_wheel")
    def test_dry_run(self, mock_qtlibs, mock_extraqtmodules, mock_local_libs, mock_extract_jar):
        mock_qtlibs.return_value = self.pyside_wheel / "PySide6/Qt/lib"
        mock_extraqtmodules.return_value = []
        dependent_plugins = ["platforms_qtforandroid",
                             "platforminputcontexts_qtvirtualkeyboardplugin",
                             "iconengines_qsvgicon"]
        mock_local_libs.return_value = [], dependent_plugins
        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, ndk_path=self.ndk_path,
                                 dry_run=True, force=True)

        self.assertEqual(mock_extract_jar.call_count, 0)
        self.assertEqual(mock_qtlibs.call_count, 1)
        self.assertEqual(mock_extraqtmodules.call_count, 1)
        self.assertEqual(mock_local_libs.call_count, 1)

    @patch("deploy_lib.android.buildozer.BuildozerConfig._BuildozerConfig__find_jars")
    @patch("deploy_lib.android.android_config.AndroidConfig.recipes_exist")
    @patch("deploy_lib.android.android_config.AndroidConfig._find_dependent_qt_modules")
    @patch("deploy_lib.android.android_config.find_qtlibs_in_wheel")
    def test_config(self, mock_qtlibs, mock_extraqtmodules, mock_recipes_exist, mock_find_jars,
                    mock_extract_jar):
        jar_dir = "tmp/jar/PySide6/jar"
        mock_extract_jar.return_value = Path(jar_dir)
        mock_qtlibs.return_value = self.pyside_wheel / "PySide6/Qt/lib"
        mock_extraqtmodules.return_value = []
        mock_recipes_exist.return_value = True
        jars, init_classes = ["/tmp/jar/PySide6/jar/Qt6Android.jar",
                              "/tmp/jar/PySide6/jar/Qt6AndroidBindings.jar"], []
        mock_find_jars.return_value = jars, init_classes

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, ndk_path=self.ndk_path,
                                 init=True, force=True, keep_deployment_files=True)

        self.assertEqual(mock_extract_jar.call_count, 1)
        self.assertEqual(mock_qtlibs.call_count, 1)
        self.assertEqual(mock_extraqtmodules.call_count, 1)
        self.assertEqual(mock_recipes_exist.call_count, 1)
        self.assertEqual(mock_find_jars.call_count, 1)
        self.assertTrue(self.config_file.exists())
        self.assertTrue(self.buildozer_config.exists())

        # test config file contents
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "main.py")
        self.assertEqual(config_obj.get_value("python", "android_packages"),
                         "buildozer==1.5.0,cython==0.29.33")
        self.assertEqual(config_obj.get_value("android", "wheel_pyside"),
                         str(self.pyside_wheel.resolve()))
        self.assertEqual(config_obj.get_value("android", "wheel_shiboken"),
                         str(self.shiboken_wheel.resolve()))
        self.assertEqual(config_obj.get_value("buildozer", "mode"), "debug")
        self.assertEqual(config_obj.get_value("buildozer", "recipe_dir"),
                         '')
        self.assertEqual(config_obj.get_value("buildozer", "jars_dir"),
                         str(self.temp_example / jar_dir))
        self.assertIn(str(self.ndk_path), config_obj.get_value("buildozer", "ndk_path"))
        self.assertEqual(config_obj.get_value("buildozer", "sdk_path"), '')
        expected_modules = {"Core", "Gui"}
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        expected_local_libs = ""
        self.assertEqual(config_obj.get_value("buildozer", "local_libs"),
                         expected_local_libs)
        self.assertEqual(config_obj.get_value("buildozer", "arch"), "x86_64")

        # test buildozer config file contents
        buildozer_config_obj = self.deploy_lib.BaseConfig(config_file=self.buildozer_config)
        obtained_jars = set(buildozer_config_obj.get_value("app", "android.add_jars").split(','))
        expected_jars = set(jars)
        self.assertEqual(obtained_jars, expected_jars)
        obtained_extra_args = buildozer_config_obj.get_value("app", "p4a.extra_args")
        extra_args_patrn = re.compile("--qt-libs=(?P<modules>.*) --load-local-libs="
                                      "(?P<local_libs>.*) --init-classes=(?P<init_classes>.*)")
        match = extra_args_patrn.search(obtained_extra_args)
        obtained_modules = match.group("modules").split(',')
        obtained_local_libs = match.group("local_libs")
        obtained_init_classes = match.group("init_classes")
        self.assertEqual(set(obtained_modules), expected_modules)
        self.assertEqual(obtained_local_libs, expected_local_libs)
        self.assertEqual(obtained_init_classes, '')
        expected_include_exts = "py,png,jpg,kv,atlas,qml,js"
        obtained_include_exts = buildozer_config_obj.get_value("app", "source.include_exts")
        self.assertEqual(expected_include_exts, obtained_include_exts)

        self.config_file.unlink()
        self.buildozer_config.unlink()

    def test_errors(self, mock_extract_jar):
        # test if error raises for non existing NDK
        with self.assertRaises(FileNotFoundError) as context:
            self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                     pyside_wheel=self.pyside_wheel, force=True)
        self.assertTrue("Unable to find Android NDK" in str(context.exception))

        # test when cwd() is not project_dir
        os.chdir(self.current_dir)
        with self.assertRaises(RuntimeError) as context:
            self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                     pyside_wheel=self.pyside_wheel, init=True, force=True)
        self.assertTrue("For Android deployment to work" in str(context.exception))


@patch("deploy_lib.config.run_qmlimportscanner")
@patch("deploy_lib.android.android_config.extract_and_copy_jar")
class TestPySide6AndroidDeployQml(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # setting up example
        example_qml_application = cls.example_root / "quick" / "models" / "stringlistmodel"
        cls.temp_qml_example = Path(
            shutil.copytree(example_qml_application, Path(cls.temp_dir) / "stringlistmodel")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_qml_example)
        self.config_file = self.temp_qml_example / "pysidedeploy.spec"
        self.buildozer_config_file = self.temp_qml_example / "buildozer.spec"
        (self.temp_qml_example / "stringlistmodel.py").rename(self.temp_qml_example / "main.py")
        (self.temp_qml_example / "stringlistmodel.pyproject").unlink()

    @patch("deploy_lib.android.android_config.AndroidConfig._find_local_libs")
    @patch("deploy_lib.android.buildozer.BuildozerConfig._BuildozerConfig__find_jars")
    @patch("deploy_lib.android.android_config.AndroidConfig.recipes_exist")
    @patch("deploy_lib.android.android_config.AndroidConfig._find_dependent_qt_modules")
    @patch("deploy_lib.android.android_config.find_qtlibs_in_wheel")
    def test_config_with_Qml(self, mock_qtlibs, mock_extraqtmodules, mock_recipes_exist,
                             mock_find_jars, mock_local_libs, mock_extract_jar,
                             mock_qmlimportscanner):
        # setting up mocks
        jar_dir = "tmp/jar/PySide6/jar"
        mock_extract_jar.return_value = Path(jar_dir)
        mock_qtlibs.return_value = self.pyside_wheel / "PySide6/Qt/lib"
        mock_extraqtmodules.return_value = ['Qml', 'Network', 'QmlModels', 'OpenGL']
        mock_recipes_exist.return_value = True
        jars, init_classes = ["/tmp/jar/PySide6/jar/Qt6Android.jar",
                              "/tmp/jar/PySide6/jar/Qt6AndroidBindings.jar",
                              "/tmp/jar/PySide6/jar/Qt6AndroidNetworkInformationBackend.jar",
                              "/tmp/jar/PySide6/jar/Qt6AndroidNetwork.jar"], []
        mock_find_jars.return_value = jars, init_classes
        dependent_plugins = ["platforms_qtforandroid",
                             "platforminputcontexts_qtvirtualkeyboardplugin",
                             "iconengines_qsvgicon"]
        mock_local_libs.return_value = [], dependent_plugins
        mock_qmlimportscanner.return_value = ["QtQuick"]

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, ndk_path=self.ndk_path,
                                 init=True, force=True, keep_deployment_files=True)

        self.assertEqual(mock_extract_jar.call_count, 1)
        self.assertEqual(mock_qtlibs.call_count, 1)
        self.assertEqual(mock_extraqtmodules.call_count, 1)
        self.assertEqual(mock_recipes_exist.call_count, 1)
        self.assertEqual(mock_find_jars.call_count, 1)
        self.assertEqual(mock_qmlimportscanner.call_count, 1)
        self.assertTrue(self.config_file.exists())
        self.assertTrue(self.buildozer_config_file.exists())

        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        expected_modules = {"Quick", "Core", "Gui", "Network", "Qml", "QmlModels", "OpenGL"}
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)
        expected_local_libs = ""
        self.assertEqual(config_obj.get_value("buildozer", "local_libs"),
                         expected_local_libs)
        expected_qt_plugins = set(dependent_plugins)
        obtained_qt_plugins = set(config_obj.get_value("android", "plugins").split(","))
        self.assertEqual(expected_qt_plugins, obtained_qt_plugins)

        # test buildozer config file contents
        buildozer_config_obj = self.deploy_lib.BaseConfig(config_file=self.buildozer_config_file)
        obtained_jars = set(buildozer_config_obj.get_value("app", "android.add_jars").split(','))
        expected_jars = set(jars)
        self.assertEqual(obtained_jars, expected_jars)
        obtained_extra_args = buildozer_config_obj.get_value("app", "p4a.extra_args")
        extra_args_patrn = re.compile("--qt-libs=(?P<modules>.*) --load-local-libs="
                                      "(?P<local_libs>.*) --init-classes=(?P<init_classes>.*)")
        match = extra_args_patrn.search(obtained_extra_args)
        obtained_modules = match.group("modules").split(',')
        obtained_local_libs = match.group("local_libs")
        obtained_init_classes = match.group("init_classes")
        self.assertEqual(set(obtained_modules), expected_modules)
        self.assertEqual(obtained_local_libs, expected_local_libs)
        self.assertEqual(obtained_init_classes, '')

        self.config_file.unlink()
        self.buildozer_config_file.unlink()


if __name__ == "__main__":
    unittest.main()
