# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import logging

from typing import List
from pathlib import Path

from . import extract_and_copy_jar, get_wheel_android_arch
from .. import Config, find_pyside_modules

ANDROID_NDK_VERSION = "25c"
ANDROID_DEPLOY_CACHE = Path.home() / ".pyside6_android_deploy"


class AndroidConfig(Config):
    """
    Wrapper class around pysidedeploy.spec file for pyside6-android-deploy
    """
    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 android_data, existing_config_file: bool = False,
                 extra_ignore_dirs: List[str] = None):
        super().__init__(config_file=config_file, source_file=source_file, python_exe=python_exe,
                         dry_run=dry_run, existing_config_file=existing_config_file)

        self.extra_ignore_dirs = extra_ignore_dirs

        if android_data.wheel_pyside:
            self.wheel_pyside = android_data.wheel_pyside
        else:
            wheel_pyside_temp = self.get_value("android", "wheel_pyside")
            if not wheel_pyside_temp:
                raise RuntimeError("[DEPLOY] Unable to find PySide6 Android wheel")
            self.wheel_pyside = Path(wheel_pyside_temp).resolve()

        if android_data.wheel_shiboken:
            self.wheel_shiboken = android_data.wheel_shiboken
        else:
            wheel_shiboken_temp = self.get_value("android", "wheel_shiboken")
            if not wheel_shiboken_temp:
                raise RuntimeError("[DEPLOY] Unable to find shiboken6 Android wheel")
            self.wheel_shiboken = Path(wheel_shiboken_temp).resolve()

        self.ndk_path = None
        if android_data.ndk_path:
            # from cli
            self.ndk_path = android_data.ndk_path
        else:
            # from config
            ndk_path_temp = self.get_value("buildozer", "ndk_path")
            if ndk_path_temp:
                self.ndk_path = Path(ndk_path_temp)
            else:
                ndk_path_temp = (ANDROID_DEPLOY_CACHE / "android-ndk"
                                 / f"android-ndk-r{ANDROID_NDK_VERSION}")
                if ndk_path_temp.exists():
                    self.ndk_path = ndk_path_temp

        if self.ndk_path:
            print(f"Using Android NDK: {str(self.ndk_path)}")
        else:
            raise FileNotFoundError("[DEPLOY] Unable to find Android NDK. Please pass the NDK "
                                    "path either from the CLI or from pysidedeploy.spec")

        self.sdk_path = None
        if android_data.sdk_path:
            self.sdk_path = android_data.sdk_path
        else:
            sdk_path_temp = self.get_value("buildozer", "sdk_path")
            if sdk_path_temp:
                self.sdk_path = Path(sdk_path_temp)
            else:
                sdk_path_temp = ANDROID_DEPLOY_CACHE / "android-sdk"
                if sdk_path_temp.exists():
                    self.sdk_path = sdk_path_temp
                else:
                    logging.info("[DEPLOY] Use default SDK from buildozer")

        if self.sdk_path:
            print(f"Using Android SDK: {str(self.sdk_path)}")

        recipe_dir_temp = self.get_value("buildozer", "recipe_dir")
        self.recipe_dir = Path(recipe_dir_temp) if recipe_dir_temp else None

        self._jars_dir = []
        jars_dir_temp = self.get_value("buildozer", "jars_dir")
        if jars_dir_temp and Path(jars_dir_temp).resolve().exists():
            self.jars_dir = Path(jars_dir_temp).resolve()

        self._modules = []
        if self.get_value("buildozer", "modules"):
            self.modules = self.get_value("buildozer", "modules").split(",")
        else:
            self._find_and_set_pysidemodules()
            self._find_and_set_qtquick_modules()

        self._arch = None
        if self.get_value("buildozer", "arch"):
            self.arch = self.get_value("buildozer", "arch")
        else:
            self._find_and_set_arch()

        self._local_libs = []
        if self.get_value("buildozer", "local_libs"):
            self.local_libs = self.get_value("buildozer", "local_libs").split(",")

        self._qt_plugins = []
        if self.get_value("android", "plugins"):
            self._qt_plugins = self.get_value("android", "plugins").split(",")

        self._mode = self.get_value("buildozer", "mode")

    @property
    def qt_plugins(self):
        return self._qt_plugins

    @qt_plugins.setter
    def qt_plugins(self, qt_plugins):
        self._qt_plugins = qt_plugins
        self.set_value("android", "plugins", ",".join(qt_plugins))

    @property
    def ndk_path(self):
        return self._ndk_path

    @ndk_path.setter
    def ndk_path(self, ndk_path: Path):
        self._ndk_path = ndk_path.resolve() if ndk_path else None
        if self._ndk_path:
            self.set_value("buildozer", "ndk_path", str(self._ndk_path))

    @property
    def sdk_path(self) -> Path:
        return self._sdk_path

    @sdk_path.setter
    def sdk_path(self, sdk_path: Path):
        self._sdk_path = sdk_path.resolve() if sdk_path else None
        if self._sdk_path:
            self.set_value("buildozer", "sdk_path", str(self._sdk_path))

    @property
    def arch(self):
        return self._arch

    @arch.setter
    def arch(self, arch):
        self._arch = arch
        self.set_value("buildozer", "arch", arch)

    @property
    def mode(self):
        return self._mode

    @property
    def modules(self):
        return self._modules

    @modules.setter
    def modules(self, modules):
        self._modules = modules
        self.set_value("buildozer", "modules", ",".join(modules))

    @property
    def local_libs(self):
        return self._local_libs

    @local_libs.setter
    def local_libs(self, local_libs):
        self._local_libs = local_libs
        self.set_value("buildozer", "local_libs", ",".join(local_libs))

    @property
    def recipe_dir(self):
        return self._recipe_dir

    @recipe_dir.setter
    def recipe_dir(self, recipe_dir: Path):
        self._recipe_dir = recipe_dir.resolve() if recipe_dir else None
        if self._recipe_dir:
            self.set_value("buildozer", "recipe_dir", str(self._recipe_dir))

    def recipes_exist(self):
        if not self._recipe_dir:
            return False

        pyside_recipe_dir = Path(self.recipe_dir) / "PySide6"
        shiboken_recipe_dir = Path(self.recipe_dir) / "shiboken6"

        return pyside_recipe_dir.is_dir() and shiboken_recipe_dir.is_dir()

    @property
    def jars_dir(self) -> Path:
        return self._jars_dir

    @jars_dir.setter
    def jars_dir(self, jars_dir: Path):
        self._jars_dir = jars_dir.resolve() if jars_dir else None
        if self._jars_dir:
            self.set_value("buildozer", "jars_dir", str(self._jars_dir))

    @property
    def wheel_pyside(self) -> Path:
        return self._wheel_pyside

    @wheel_pyside.setter
    def wheel_pyside(self, wheel_pyside: Path):
        self._wheel_pyside = wheel_pyside.resolve() if wheel_pyside else None
        if self._wheel_pyside:
            self.set_value("android", "wheel_pyside", str(self._wheel_pyside))

    @property
    def wheel_shiboken(self) -> Path:
        return self._wheel_shiboken

    @wheel_shiboken.setter
    def wheel_shiboken(self, wheel_shiboken: Path):
        self._wheel_shiboken = wheel_shiboken.resolve() if wheel_shiboken else None
        if self._wheel_shiboken:
            self.set_value("android", "wheel_shiboken", str(self._wheel_shiboken))

    def _find_and_set_pysidemodules(self):
        self.modules = find_pyside_modules(project_dir=self.project_dir,
                                           extra_ignore_dirs=self.extra_ignore_dirs,
                                           project_data=self.project_data)
        logging.info("The following PySide modules were found from the python files of "
                     f"the project {self.modules}")

    def find_and_set_jars_dir(self):
        """Extract out and copy .jar files to {generated_files_path}
        """
        if not self.dry_run:
            logging.info("[DEPLOY] Extract and copy jar files from PySide6 wheel to "
                         f"{self.generated_files_path}")
            self.jars_dir = extract_and_copy_jar(wheel_path=self.wheel_pyside,
                                                 generated_files_path=self.generated_files_path)

    def _find_and_set_arch(self):
        """Find architecture from wheel name
        """
        self.arch = get_wheel_android_arch(wheel=self.wheel_pyside)
        if not self.arch:
            raise RuntimeError("[DEPLOY] PySide wheel corrupted. Wheel name should end with"
                               "platform name")

    def _find_and_set_qtquick_modules(self):
        """Identify if QtQuick is used in QML files and add them as dependency
        """
        extra_modules = []

        if "QtQuick" in self.qml_modules:
            extra_modules.append("Quick")

        if "QtQuick.Controls" in self.qml_modules:
            extra_modules.append("QuickControls2")

        self.modules += extra_modules
