# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch
from zipfile import ZipFile

PYSIDE_ROOT = Path(__file__).resolve().parents[5]
PYSIDE_TOOLS = PYSIDE_ROOT / "sources" / "pyside-tools"


def install_ios_requirements():
    """deploy_lib.ios needs the packages listed in requirements-ios.txt, which are
    not part of the general test environment. They are installed here, which is why
    nothing from deploy_lib may be imported at module or class level in this file:
    both run before the first setUpClass."""
    ios_requirements_file = PYSIDE_TOOLS / "requirements-ios.txt"
    with open(ios_requirements_file, 'r', encoding='UTF-8') as file:
        while line := file.readline():
            dependent_package = line.rstrip().split('==')[0]
            if not bool(importlib.util.find_spec(dependent_package)):
                command = [sys.executable, "-m", "pip", "install", dependent_package]
                subprocess.run(command)

    if str(PYSIDE_TOOLS) not in sys.path:
        sys.path.append(str(PYSIDE_TOOLS))


class IosHelperTestBase(unittest.TestCase):
    """Base for the tests covering the helper functions of deploy_lib.ios."""

    @classmethod
    def setUpClass(cls):
        install_ios_requirements()
        cls.ios_config = importlib.import_module("deploy_lib.ios.ios_config")
        cls.ios_helper = importlib.import_module("deploy_lib.ios.ios_helper")


class TestGetWheelIosTarget(IosHelperTestBase):
    """Parsing the (arch, simulator) target out of an iOS wheel's platform tag."""

    def test_device_arm64(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-ios_arm64.whl")
        self.assertEqual(self.ios_helper.get_wheel_ios_target(wheel), ("arm64", False))

    def test_simulator_arm64(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-ios_arm64_simulator.whl")
        self.assertEqual(self.ios_helper.get_wheel_ios_target(wheel), ("arm64", True))

    def test_simulator_x86_64(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-ios_x86_64_simulator.whl")
        self.assertEqual(self.ios_helper.get_wheel_ios_target(wheel), ("x86_64", True))

    def test_no_platform_tag(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-manylinux_x86_64.whl")
        self.assertIsNone(self.ios_helper.get_wheel_ios_target(wheel))

    def test_unsupported_arch(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-ios_armv7.whl")
        self.assertIsNone(self.ios_helper.get_wheel_ios_target(wheel))

    def test_wrong_case(self):
        wheel = Path("PySide6-6.12.0-cp315-cp315-IOS_ARM64.whl")
        self.assertIsNone(self.ios_helper.get_wheel_ios_target(wheel))

    def test_trailing_garbage_after_tag(self):
        # the tag must be anchored at the end of the stem
        wheel = Path("PySide6-6.12.0-cp315-cp315-ios_arm64_simulator_extra.whl")
        self.assertIsNone(self.ios_helper.get_wheel_ios_target(wheel))


class TestGetXcframeworkPythonVersion(IosHelperTestBase):
    """Parsing the bundled Python version out of Python.xcframework/lib/."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.xcframework_path = Path(self.tmp.name) / "Python.xcframework"

    def tearDown(self):
        self.tmp.cleanup()

    def _make_lib_entry(self, name: str):
        lib_dir = self.xcframework_path / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / name).mkdir()

    def test_valid_version_dir(self):
        self._make_lib_entry("python3.15")
        self.assertEqual(self.ios_helper.get_xcframework_python_version(self.xcframework_path),
                         "3.15")

    def test_missing_lib_dir(self):
        self.assertIsNone(self.ios_helper.get_xcframework_python_version(self.xcframework_path))

    def test_lib_dir_with_no_match(self):
        self._make_lib_entry("include")
        self.assertIsNone(self.ios_helper.get_xcframework_python_version(self.xcframework_path))

    def test_patch_version_does_not_match(self):
        # fullmatch requires exactly "python<major>.<minor>", nothing more
        self._make_lib_entry("python3.14.2")
        self.assertIsNone(self.ios_helper.get_xcframework_python_version(self.xcframework_path))

    def test_missing_minor_version_does_not_match(self):
        self._make_lib_entry("python3")
        self.assertIsNone(self.ios_helper.get_xcframework_python_version(self.xcframework_path))


class TestQtDeploymentTarget(IosHelperTestBase):
    """Parsing CMAKE_OSX_DEPLOYMENT_TARGET out of Qt's own toolchain file."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.qt_ios = Path(self.tmp.name)
        self.toolchain = self.qt_ios / "lib" / "cmake" / "Qt6" / "qt.toolchain.cmake"
        self.toolchain.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_toolchain_file(self):
        self.assertIsNone(self.ios_config._qt_deployment_target(self.qt_ios))

    def test_valid_line(self):
        self.toolchain.write_text('set(CMAKE_OSX_DEPLOYMENT_TARGET "18.0" CACHE STRING "")\n')
        self.assertEqual(self.ios_config._qt_deployment_target(self.qt_ios), "18.0")

    def test_key_absent(self):
        self.toolchain.write_text('set(CMAKE_SOME_OTHER_VAR "18.0")\n')
        self.assertIsNone(self.ios_config._qt_deployment_target(self.qt_ios))

    def test_value_missing_quotes(self):
        self.toolchain.write_text('set(CMAKE_OSX_DEPLOYMENT_TARGET 18.0)\n')
        self.assertIsNone(self.ios_config._qt_deployment_target(self.qt_ios))

    def test_empty_file(self):
        self.toolchain.write_text('')
        self.assertIsNone(self.ios_config._qt_deployment_target(self.qt_ios))


class TestSlicePlatform(IosHelperTestBase):
    """Parsing the LC_BUILD_VERSION platform code out of `otool -l` output."""

    def setUp(self):
        self.binary = Path("/tmp/dummy/QtCore")

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_device_platform(self, mock_run):
        mock_run.return_value.stdout = (
            "Load command 12\n"
            "      cmd LC_BUILD_VERSION\n"
            "  cmdsize 24\n"
            " platform 2\n"
        )
        self.assertEqual(self.ios_config._slice_platform(self.binary, "arm64"), 2)

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_simulator_platform(self, mock_run):
        mock_run.return_value.stdout = (
            "      cmd LC_BUILD_VERSION\n"
            "  cmdsize 24\n"
            " platform 7\n"
        )
        self.assertEqual(self.ios_config._slice_platform(self.binary, "arm64"), 7)

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_arch_slice_missing_from_binary(self, mock_run):
        # otool exits non-zero when the requested -arch slice isn't present
        mock_run.side_effect = subprocess.CalledProcessError(1, ["otool"])
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "arm64"))

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_otool_not_installed(self, mock_run):
        mock_run.side_effect = OSError("otool not found")
        with self.assertRaises(ValueError):
            self.ios_config._slice_platform(self.binary, "arm64")

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_output_without_lc_build_version(self, mock_run):
        mock_run.return_value.stdout = "Load command 3\n      cmd LC_SEGMENT_64\n"
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "arm64"))
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "x86_64"))

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_output_missing_platform_line(self, mock_run):
        mock_run.return_value.stdout = "      cmd LC_BUILD_VERSION\n  cmdsize 24\n"
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "arm64"))
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "x86_64"))

    @patch("deploy_lib.ios.ios_config.subprocess.run")
    def test_empty_output(self, mock_run):
        mock_run.return_value.stdout = ""
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "arm64"))
        self.assertIsNone(self.ios_config._slice_platform(self.binary, "x86_64"))


class TestCheckBinaryMatchesTarget(IosHelperTestBase):
    """The higher-level check that raises when a Mach-O slice doesn't
    match the requested (arch, simulator) target."""

    def setUp(self):
        self.binary = Path("/tmp/dummy/QtCore")

    @patch("deploy_lib.ios.ios_config._slice_platform")
    def test_matching_device_target(self, mock_slice):
        mock_slice.return_value = 2  # _PLATFORM_IOS
        self.ios_config._check_binary_matches_target(self.binary, "arm64",
                                                     simulator=False, what="Qt")

    @patch("deploy_lib.ios.ios_config._slice_platform")
    def test_matching_simulator_target(self, mock_slice):
        mock_slice.return_value = 7  # _PLATFORM_IOS_SIMULATOR
        self.ios_config._check_binary_matches_target(self.binary, "arm64",
                                                     simulator=True, what="Qt")

    @patch("deploy_lib.ios.ios_config._slice_platform")
    def test_missing_arch_slice_raises(self, mock_slice):
        mock_slice.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.ios_config._check_binary_matches_target(self.binary, "arm64",
                                                         simulator=False, what="Qt")
        self.assertIn("does not contain an arm64 slice", str(ctx.exception))

    @patch("deploy_lib.ios.ios_config._slice_platform")
    def test_device_binary_for_simulator_target_raises(self, mock_slice):
        mock_slice.return_value = 2  # built for device
        with self.assertRaises(ValueError) as ctx:
            self.ios_config._check_binary_matches_target(self.binary, "arm64",
                                                         simulator=True, what="Qt")
        self.assertIn("built for device, not simulator", str(ctx.exception))

    @patch("deploy_lib.ios.ios_config._slice_platform")
    def test_unknown_platform_code_raises(self, mock_slice):
        mock_slice.return_value = 99  # neither device nor simulator
        with self.assertRaises(ValueError) as ctx:
            self.ios_config._check_binary_matches_target(self.binary, "arm64",
                                                         simulator=False, what="Qt")
        self.assertIn("platform 99", str(ctx.exception))


class TestDefaultBundleId(IosHelperTestBase):
    """Sanitizing an app name down to an Xcode-style placeholder bundle id."""

    def test_alphanumeric_name(self):
        self.assertEqual(self.ios_config._default_bundle_id("MyApp"), "com.example.MyApp")

    def test_hyphen_is_kept(self):
        self.assertEqual(self.ios_config._default_bundle_id("My-App"), "com.example.My-App")

    def test_strips_non_alphanumeric_non_hyphen(self):
        self.assertEqual(self.ios_config._default_bundle_id("My-App! 2.0"), "com.example.My-App20")

    def test_strips_leading_and_trailing_hyphens(self):
        self.assertEqual(self.ios_config._default_bundle_id("-My App-"), "com.example.MyApp")

    def test_empty_after_sanitizing_falls_back(self):
        self.assertEqual(self.ios_config._default_bundle_id("---"), "com.example.App")

    def test_empty_name_falls_back(self):
        self.assertEqual(self.ios_config._default_bundle_id(""), "com.example.App")


class DeployTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyside_root = PYSIDE_ROOT
        cls.example_root = cls.pyside_root / "examples"
        cls.temp_dir = tempfile.mkdtemp()
        temp_dir = Path(cls.temp_dir)
        cls.current_dir = Path.cwd()
        cls.pyside_wheel = temp_dir / "pyside6-6.12.0a1-6.12.0-cp315-cp315-ios_arm64.whl"
        cls._build_dummy_pyside_wheel(cls.pyside_wheel)
        cls.shiboken_wheel = temp_dir / "shiboken6-6.12.0a1-6.12.0-cp315-cp315-ios_arm64.whl"
        cls.xcframework_path = temp_dir / "Python.xcframework"
        (cls.xcframework_path / "lib" / "python3.15").mkdir(parents=True)

        install_ios_requirements()

        cls.deploy_lib = importlib.import_module("deploy_lib")
        cls.ios_deploy = importlib.import_module("ios_deploy")
        sys.modules["ios_deploy"] = cls.ios_deploy

        # required for comparing long strings
        cls.maxDiff = None

        # print no outputs to stdout
        sys.stdout = mock.MagicMock()

    @staticmethod
    def _build_dummy_pyside_wheel(wheel_path: Path):
        """A minimal PySide6 wheel: just enough for IOSConfig.__init__ to unpack it
        and find a Qt-for-iOS kit with a toolchain file and a dummy QtCore binary"""
        with ZipFile(wheel_path, "w") as archive:
            archive.writestr("PySide6/Qt/lib/QtCore.framework/QtCore", b"")
            archive.writestr(
                "PySide6/Qt/lib/cmake/Qt6/qt.toolchain.cmake",
                'set(CMAKE_OSX_DEPLOYMENT_TARGET "18.0" CACHE STRING "")\n',
            )

    def tearDown(self) -> None:
        super().tearDown()
        os.chdir(self.current_dir)
        shutil.rmtree(self.temp_example / "deployment", ignore_errors=True)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(Path(cls.temp_dir))


@patch("deploy_lib.ios.ios_config._check_binary_matches_target")
class TestPySide6IosDeployWidgets(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_widget_application = cls.example_root / "widgets" / "widgetsgallery"
        cls.temp_example = Path(
            shutil.copytree(example_widget_application, Path(cls.temp_dir) / "widgetsgallery")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example)
        self.config_file = self.temp_example / "pysidedeploy.spec"

    @patch("deploy_lib.ios.ios_dependency.resolve_qml_plugins")
    @patch("deploy_lib.ios.ios_dependency.enabled_plugins")
    @patch("deploy_lib.ios.ios_dependency.resolve_qt_dependencies")
    @patch("deploy_lib.ios.main_mm.generate")
    @patch("deploy_lib.ios.info_plist.generate")
    @patch("deploy_lib.ios.pbxproj.generate")
    def test_config(self, mock_pbxproj, mock_info_plist, mock_main_mm, mock_resolve_deps,
                    mock_enabled_plugins, mock_resolve_qml, mock_check_binary):
        mock_resolve_qml.return_value = []
        mock_enabled_plugins.return_value = []
        mock_resolve_deps.return_value = mock.MagicMock()
        mock_main_mm.return_value = "// generated main.mm"
        mock_info_plist.return_value = b"<plist/>"
        mock_pbxproj.return_value = "// generated project.pbxproj"

        self.ios_deploy.main(name="iosApp", wheel_pyside=self.pyside_wheel,
                             wheel_shiboken=self.shiboken_wheel,
                             xcframework_path=self.xcframework_path)

        self.assertEqual(mock_check_binary.call_count, 1)
        self.assertEqual(mock_resolve_qml.call_count, 1)
        self.assertEqual(mock_enabled_plugins.call_count, 1)
        self.assertEqual(mock_resolve_deps.call_count, 1)
        self.assertEqual(mock_main_mm.call_count, 1)
        self.assertEqual(mock_info_plist.call_count, 1)
        self.assertEqual(mock_pbxproj.call_count, 1)

        self.assertTrue(self.config_file.exists())
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)

        self.assertEqual(config_obj.get_value("ios", "wheel_pyside"),
                         str(self.pyside_wheel.resolve()))
        self.assertEqual(config_obj.get_value("ios", "wheel_shiboken"),
                         str(self.shiboken_wheel.resolve()))
        self.assertEqual(config_obj.get_value("ios", "xcframework_path"),
                         str(self.xcframework_path.resolve()))
        self.assertEqual(config_obj.get_value("ios", "bundle_id"), "com.example.iosApp")

        expected_modules = {"Core", "Gui", "Widgets"}
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)

        out_dir = self.temp_example / "deployment"
        self.assertEqual((out_dir / "main.mm").read_text(), "// generated main.mm")
        self.assertEqual((out_dir / "Info.plist").read_bytes(), b"<plist/>")
        pbxproj_path = out_dir / "iosApp.xcodeproj" / "project.pbxproj"
        self.assertEqual(pbxproj_path.read_text(), "// generated project.pbxproj")

        self.config_file.unlink()

    def test_downloads_xcframework_when_not_provided(self, mock_check_binary):
        with patch("deploy_lib.ios.ios_config.download_python_support") as mock_download:
            mock_download.return_value = self.xcframework_path
            self.ios_deploy.main(name="iosApp", wheel_pyside=self.pyside_wheel,
                                 wheel_shiboken=self.shiboken_wheel, init=True)
            self.assertEqual(mock_download.call_count, 1)

        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)
        self.assertEqual(config_obj.get_value("ios", "xcframework_path"),
                         str(self.xcframework_path.resolve()))
        self.config_file.unlink()

    def test_missing_wheel_shiboken(self, mock_check_binary):
        with patch("builtins.print") as mock_print:
            self.ios_deploy.main(name="iosApp", wheel_pyside=self.pyside_wheel,
                                 xcframework_path=self.xcframework_path, init=True)
        printed = " ".join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Unable to find shiboken6 iOS wheel", printed)
        self.config_file.unlink()

    def test_missing_wheel_pyside(self, mock_check_binary):
        with patch("builtins.print") as mock_print:
            self.ios_deploy.main(name="iosApp", wheel_shiboken=self.shiboken_wheel,
                                 xcframework_path=self.xcframework_path, init=True)
        printed = " ".join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Unable to find PySide6 iOS wheel", printed)
        self.config_file.unlink()


@patch("deploy_lib.config.run_qmlimportscanner")
@patch("deploy_lib.ios.ios_config._check_binary_matches_target")
class TestPySide6IosDeployQml(DeployTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        example_widget_application = cls.example_root / "quickcontrols" / "contactslist"
        cls.temp_example = Path(
            shutil.copytree(example_widget_application, Path(cls.temp_dir) / "contactslist")
        ).resolve()

    def setUp(self):
        os.chdir(self.temp_example)
        self.config_file = self.temp_example / "pysidedeploy.spec"

    @patch("deploy_lib.ios.ios_dependency.resolve_qml_plugins")
    @patch("deploy_lib.ios.ios_dependency.enabled_plugins")
    @patch("deploy_lib.ios.ios_dependency.resolve_qt_dependencies")
    @patch("deploy_lib.ios.main_mm.generate")
    @patch("deploy_lib.ios.info_plist.generate")
    @patch("deploy_lib.ios.pbxproj.generate")
    def test_config(self, mock_pbxproj, mock_info_plist, mock_main_mm, mock_resolve_deps,
                    mock_enabled_plugins, mock_resolve_qml, mock_check_binary,
                    mock_qmlimportscanner):
        mock_resolve_qml.return_value = []
        mock_enabled_plugins.return_value = []
        mock_resolve_deps.return_value = mock.MagicMock()
        mock_main_mm.return_value = "// generated main.mm"
        mock_info_plist.return_value = b"<plist/>"
        mock_pbxproj.return_value = "// generated project.pbxproj"

        self.ios_deploy.main(name="iosApp", wheel_pyside=self.pyside_wheel,
                             wheel_shiboken=self.shiboken_wheel,
                             xcframework_path=self.xcframework_path)

        self.assertEqual(mock_check_binary.call_count, 1)
        self.assertEqual(mock_resolve_qml.call_count, 1)
        self.assertEqual(mock_enabled_plugins.call_count, 1)
        self.assertEqual(mock_resolve_deps.call_count, 1)
        self.assertEqual(mock_main_mm.call_count, 1)
        self.assertEqual(mock_info_plist.call_count, 1)
        self.assertEqual(mock_pbxproj.call_count, 1)

        self.assertTrue(self.config_file.exists())
        config_obj = self.deploy_lib.BaseConfig(config_file=self.config_file)

        self.assertEqual(config_obj.get_value("ios", "wheel_pyside"),
                         str(self.pyside_wheel.resolve()))
        self.assertEqual(config_obj.get_value("ios", "wheel_shiboken"),
                         str(self.shiboken_wheel.resolve()))
        self.assertEqual(config_obj.get_value("ios", "xcframework_path"),
                         str(self.xcframework_path.resolve()))
        self.assertEqual(config_obj.get_value("ios", "bundle_id"), "com.example.iosApp")

        expected_modules = {"Core", "Gui", "Qml"}
        obtained_modules = set(config_obj.get_value("qt", "modules").split(","))
        self.assertEqual(obtained_modules, expected_modules)

        out_dir = self.temp_example / "deployment"
        self.assertEqual((out_dir / "main.mm").read_text(), "// generated main.mm")
        self.assertEqual((out_dir / "Info.plist").read_bytes(), b"<plist/>")
        pbxproj_path = out_dir / "iosApp.xcodeproj" / "project.pbxproj"
        self.assertEqual(pbxproj_path.read_text(), "// generated project.pbxproj")

        self.config_file.unlink()


if __name__ == "__main__":
    unittest.main()
