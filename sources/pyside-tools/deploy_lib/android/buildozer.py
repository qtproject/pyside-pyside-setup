# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import List

from .. import MAJOR_VERSION, BaseConfig, Config, run_command


class BuildozerConfig(BaseConfig):
    def __init__(self, buildozer_spec_file: Path, pysidedeploy_config: Config):
        super().__init__(buildozer_spec_file, comment_prefixes="#")
        self.set_value("app", "title", pysidedeploy_config.title)
        self.set_value("app", "package.name", pysidedeploy_config.title)
        self.set_value("app", "package.domain",
                       f"org.{pysidedeploy_config.title}")

        include_exts = self.get_value("app", "source.include_exts")
        include_exts = f"{include_exts},qml"
        self.set_value("app", "source.include_exts", include_exts, raise_warning=False)

        self.set_value("app", "requirements", "python3,shiboken6,PySide6")

        # android platform specific
        if pysidedeploy_config.ndk_path:
            self.set_value("app", "android.ndk_path", str(pysidedeploy_config.ndk_path))

        if pysidedeploy_config.sdk_path:
            self.set_value("app", "android.sdk_path", str(pysidedeploy_config.sdk_path))

        self.set_value("app", "android.add_jars", f"{str(pysidedeploy_config.jars_dir)}/*.jar")

        platform_map = {"aarch64": "arm64-v8a",
                        "armv7a": "armeabi-v7a",
                        "i686": "x86",
                        "x86_64": "x86_64"}
        self.arch = platform_map[pysidedeploy_config.arch]
        self.set_value("app", "android.archs", self.arch)

        # p4a changes
        logging.info("[DEPLOY] Using custom fork of python-for-android: "
                     "https://github.com/shyamnathp/python-for-android/tree/pyside_support")
        self.set_value("app", "p4a.fork", "shyamnathp")
        self.set_value("app", "p4a.branch", "pyside_support_2")
        self.set_value('app', "p4a.local_recipes", str(pysidedeploy_config.recipe_dir))
        self.set_value("app", "p4a.bootstrap", "qt")

        modules = ",".join(pysidedeploy_config.modules)
        local_libs = ",".join(pysidedeploy_config.local_libs)
        extra_args = (f"--qt-libs={modules} --load-local-libs={local_libs}")
        self.set_value("app", "p4a.extra_args", extra_args)

        dependency_files = self.__get_dependency_files(pysidedeploy_config)
        permissions = self.__find_permissions(dependency_files)
        permissions = ", ".join(permissions)
        self.set_value("app", "android.permissions", permissions)

        # TODO: does not work atm. Seems like a bug with buildozer
        # change buildozer build_dir
        # self.set_value("buildozer", "build_dir", str(build_dir.relative_to(Path.cwd())))

        # change final apk/aab path
        self.set_value("buildozer", "bin_dir", str(pysidedeploy_config.exe_dir.resolve()))

        self.update_config()

    def __get_dependency_files(self, pysidedeploy_config: Config) -> List[zipfile.Path]:
        """
        Based on pysidedeploy_config.modules, returns the
        Qt6{module}_{arch}-android-dependencies.xml file, which contains the various
        dependencies of the module, like permissions, plugins etc
        """
        dependency_files = []
        needed_dependency_files = [(f"Qt{MAJOR_VERSION}{module}_{self.arch}"
                                   "-android-dependencies.xml") for module in
                                   pysidedeploy_config.modules]
        archive = zipfile.ZipFile(pysidedeploy_config.wheel_pyside)

        # find parent path to dependency files in the wheel
        dependency_parent_path = None
        for file in archive.namelist():
            if file.endswith("android-dependencies.xml"):
                dependency_parent_path = Path(file).parent
                # all dependency files are in the same path
                break

        for dependency_file_name in needed_dependency_files:
            dependency_file = dependency_parent_path / dependency_file_name
            # convert from pathlib.Path to zipfile.Path
            dependency_file = zipfile.Path(archive, at=str(dependency_file))

            if dependency_file.exists():
                dependency_files.append(dependency_file)

        logging.info(f"[DEPLOY] The following dependency files were found: {*dependency_files,}")

        return dependency_files

    def __find_permissions(self, dependency_files: List[zipfile.Path]):
        permissions = set()
        for dependency_file in dependency_files:
            xml_content = dependency_file.read_text()
            root = ET.fromstring(xml_content)
            for permission in root.iter("permission"):
                permissions.add(permission.attrib['name'])
        return permissions


class Buildozer:
    dry_run = False

    @staticmethod
    def initialize(pysidedeploy_config: Config):
        project_dir = Path(pysidedeploy_config.project_dir)
        buildozer_spec = project_dir / "buildozer.spec"
        if buildozer_spec.exists():
            logging.warning(f"[DEPLOY] buildozer.spec already present in {str(project_dir)}."
                            "Using it")
            return

        # creates buildozer.spec config file
        command = ["buildozer", "init"]
        run_command(command=command, dry_run=Buildozer.dry_run)
        if not Buildozer.dry_run:
            if not buildozer_spec.exists():
                raise RuntimeError(f"buildozer.spec not found in {Path.cwd()}")
            BuildozerConfig(buildozer_spec, pysidedeploy_config)

    @staticmethod
    def create_executable(mode: str):
        command = ["buildozer", "android", mode]
        run_command(command=command, dry_run=Buildozer.dry_run)
