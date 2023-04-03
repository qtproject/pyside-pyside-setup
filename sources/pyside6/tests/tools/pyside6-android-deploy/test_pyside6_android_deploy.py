# Copyright (C) 2023 The Qt Company Ltd.
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


class TestPySide6AndroidDeploy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyside_root = Path(__file__).parents[5].resolve()
        cls.example_root = cls.pyside_root / "examples"
        example_widget_application = cls.example_root / "gui" / "analogclock"
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_example = Path(
            shutil.copytree(example_widget_application, Path(cls.temp_dir) / "analogclock")
        ).resolve()
        cls.current_dir = Path.cwd()
        cls.pyside_wheel = Path("tmp/PySide6-6.5.0a1-6.5.0-cp37-abi3-android_x86_64.whl")
        cls.shiboken_wheel = Path("tmp/shiboken6-6.5.0a1-6.5.0-cp37-abi3-android_x86_64.whl")
        cls.ndk_path = Path("tmp/android_sdk/ndk/25.2.9519653")
        cls.sdk_path = Path("tmp/android_sdk")

        sys.path.append(str(cls.pyside_root / "sources" / "pyside-tools"))
        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.android_deploy = importlib.import_module("android_deploy")
        sys.modules["android_deploy"] = cls.android_deploy

        # required for comparing long strings
        cls.maxDiff = None

        # print no outputs to stdout
        sys.stdout = mock.MagicMock()

    def setUp(self):
        os.chdir(self.temp_example)
        self.config_file = self.temp_example / "pysidedeploy.spec"

    @patch("android_deploy.extract_and_copy_jar")
    @patch("android_deploy.Wheel")
    def test_dry_run(self, mock_jar, mock_wheel):
        mock_wheel.version = "6.5.0a1"

        # test if dry_run works without errors
        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, dry_run=True, force=True)

        self.assertEqual(mock_wheel.call_count, 1)
        self.assertEqual(mock_jar.call_count, 1)
        self.assertFalse(self.config_file.exists())

    @patch("android_deploy.extract_and_copy_jar")
    @patch("android_deploy.Wheel")
    def test_config(self, mock_jar, mock_wheel):
        '''
            Tests config options from the dynamically created buildozer.spec and pysidedeploy.spec
        '''
        mock_wheel.version = "6.5.0a1"

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, init=True, force=True)

        self.assertEqual(mock_wheel.call_count, 1)
        self.assertEqual(mock_jar.call_count, 1)
        self.assertTrue(self.config_file.exists())

        # test config file contents
        config_obj = ConfigFile(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("app", "input_file"), "main.py")
        self.assertEqual(config_obj.get_value("python", "android_packages"),
                         "buildozer==1.5.0,cython==0.29.33")
        self.assertEqual(config_obj.get_value("qt", "wheel_pyside"),
                         str(self.pyside_wheel.resolve()))
        self.assertEqual(config_obj.get_value("qt", "wheel_shiboken"),
                         str(self.shiboken_wheel.resolve()))
        self.assertEqual(config_obj.get_value("buildozer", "mode"), "debug")
        self.assertEqual(config_obj.get_value("buildozer", "recipe_dir"),
                         str(self.temp_example / "deployment" / "recipes"))
        self.assertEqual(config_obj.get_value("buildozer", "jars_dir"),
                         str(self.temp_example / "deployment" / "jar" / "PySide6" / "jar"))
        self.assertEqual(config_obj.get_value("buildozer", "ndk_path"), "")
        self.assertEqual(config_obj.get_value("buildozer", "sdk_path"), "")
        self.assertEqual(config_obj.get_value("buildozer", "modules"), "Core,Gui,Widgets")
        self.assertEqual(config_obj.get_value("buildozer", "local_libs"),
                         "plugins_platforms_qtforandroid")
        self.assertEqual(config_obj.get_value("buildozer", "arch"), "x86_64")
        self.config_file.unlink()

    @patch("android_deploy.extract_and_copy_jar")
    @patch("android_deploy.Wheel")
    def test_config_with_ndk_sdk(self, mock_jar, mock_wheel):
        mock_wheel.version = "6.5.0a1"

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, ndk_path=self.ndk_path,
                                 sdk_path=self.sdk_path, init=True, force=True)

        self.assertEqual(mock_wheel.call_count, 1)
        self.assertEqual(mock_jar.call_count, 1)
        self.assertTrue(self.config_file.exists())

        # test config file contents
        config_obj = ConfigFile(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("buildozer", "ndk_path"),
                         str(self.ndk_path.resolve()))
        self.assertEqual(config_obj.get_value("buildozer", "sdk_path"),
                         str(self.sdk_path.resolve()))
        self.config_file.unlink()

    def test_error_pwd_not_projectdir(self):
        os.chdir(self.current_dir)
        with self.assertRaises(RuntimeError):
            self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                     pyside_wheel=self.pyside_wheel, init=True, force=True)

    def test_error_no_wheels(self):
        os.chdir(self.current_dir)
        with self.assertRaises(RuntimeError):
            self.android_deploy.main(name="android_app", shiboken_wheel=None,
                                     pyside_wheel=self.pyside_wheel, init=True, force=True)

    @patch("android_deploy.extract_and_copy_jar")
    @patch("android_deploy.Wheel")
    def test_config_with_Qml(self, mock_jar, mock_wheel):
        example_qml_application = self.example_root / "quick" / "models" / "stringlistmodel"
        temp_qml_example = Path(
            shutil.copytree(example_qml_application, Path(self.temp_dir) / "stringlistmodel")
        ).resolve()
        config_file = temp_qml_example / "pysidedeploy.spec"
        (temp_qml_example / "stringlistmodel.py").rename(temp_qml_example / "main.py")
        (temp_qml_example / "stringlistmodel.pyproject").unlink()
        os.chdir(temp_qml_example)

        mock_wheel.version = "6.5.0a1"

        self.android_deploy.main(name="android_app", shiboken_wheel=self.shiboken_wheel,
                                 pyside_wheel=self.pyside_wheel, init=True, force=True)

        self.assertEqual(mock_wheel.call_count, 1)
        self.assertEqual(mock_jar.call_count, 1)
        self.assertTrue(config_file.exists())

        # test config file contents
        config_obj = ConfigFile(config_file=config_file)
        self.assertEqual(config_obj.get_value("buildozer", "modules"),
                         "Core,Gui,Widgets,Network,OpenGL,Qml,Quick,QuickControls2")
        config_file.unlink()

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


if __name__ == "__main__":
    unittest.main()
