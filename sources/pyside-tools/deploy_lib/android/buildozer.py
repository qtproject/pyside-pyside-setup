# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
import logging
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from . import AndroidConfig
from .. import BaseConfig, run_command


class BuildozerConfig(BaseConfig):
    def __init__(self, buildozer_spec_file: Path, pysidedeploy_config: AndroidConfig):
        super().__init__(buildozer_spec_file, comment_prefixes="#")
        self.set_value("app", "title", pysidedeploy_config.title)
        self.set_value("app", "package.name", pysidedeploy_config.title)
        self.set_value("app", "package.domain",
                       f"org.{pysidedeploy_config.title}")

        include_exts = self.get_value("app", "source.include_exts")
        include_exts = f"{include_exts},qml,js"
        self.set_value("app", "source.include_exts", include_exts, raise_warning=False)

        self.set_value("app", "requirements", "python3,shiboken6,PySide6")

        # android platform specific
        if pysidedeploy_config.ndk_path:
            self.set_value("app", "android.ndk_path", str(pysidedeploy_config.ndk_path))

        if pysidedeploy_config.sdk_path:
            self.set_value("app", "android.sdk_path", str(pysidedeploy_config.sdk_path))

        self.set_value("app", "android.archs", pysidedeploy_config.arch)

        # p4a changes
        self.set_value("app", "p4a.bootstrap", "qt")
        self.set_value('app', "p4a.local_recipes", str(pysidedeploy_config.recipe_dir))

        # add p4a branch
        # by default the master branch is used
        # https://github.com/kivy/python-for-android/commit/b92522fab879dbfc0028966ca3c59ef46ab7767d
        # has not been merged to master yet. So, we use the develop branch for now
        # TODO: remove this once the above commit is merged to master
        self.set_value("app", "p4a.branch", "develop")

        # add permissions
        permissions = self.__find_permissions(pysidedeploy_config.dependency_files)
        permissions = ", ".join(permissions)
        self.set_value("app", "android.permissions", permissions)

        # add jars and initClasses for the jars
        jars, init_classes = self.__find_jars(pysidedeploy_config.dependency_files,
                                              pysidedeploy_config.jars_dir)
        self.set_value("app", "android.add_jars", ",".join(jars))

        # extra arguments specific to Qt
        modules = ",".join(pysidedeploy_config.modules)
        local_libs = ",".join(pysidedeploy_config.local_libs)
        init_classes = ",".join(init_classes)
        extra_args = (f"--qt-libs={modules} --load-local-libs={local_libs}"
                      f" --init-classes={init_classes}")
        self.set_value("app", "p4a.extra_args", extra_args)

        # TODO: does not work atm. Seems like a bug with buildozer
        # change buildozer build_dir
        # self.set_value("buildozer", "build_dir", str(build_dir.relative_to(Path.cwd())))

        # change final apk/aab path
        self.set_value("buildozer", "bin_dir", str(pysidedeploy_config.exe_dir.resolve()))

        # set application icon
        self.set_value("app", "icon.filename", pysidedeploy_config.icon)

        self.update_config()

    def __find_permissions(self, dependency_files: list[zipfile.Path]):
        permissions = set()
        for dependency_file in dependency_files:
            xml_content = dependency_file.read_text()
            root = ET.fromstring(xml_content)
            for permission in root.iter("permission"):
                permissions.add(permission.attrib['name'])
        return permissions

    def __find_jars(self, dependency_files: list[zipfile.Path], jars_dir: Path):
        jars, init_classes = set(), set()
        for dependency_file in dependency_files:
            xml_content = dependency_file.read_text()
            root = ET.fromstring(xml_content)
            for jar in root.iter("jar"):
                jar_file = jar.attrib['file']
                if jar_file.startswith("jar/"):
                    jar_file_name = jar_file[4:]
                    if (jars_dir / jar_file_name).exists():
                        jars.add(str(jars_dir / jar_file_name))
                    else:
                        logging.warning(f"[DEPLOY] Unable to include {jar_file}. "
                                        f"{jar_file} does not exist in {jars_dir}")
                        continue
                else:
                    logging.warning(f"[DEPLOY] Unable to include {jar_file}. "
                                    "All jar file paths should begin with 'jar/'")
                    continue

                jar_init_class = jar.attrib.get('initClass')
                if jar_init_class:
                    init_classes.add(jar_init_class)

        # add the jar with all the activity and service java files
        # this is created from Qt for Python instead of Qt
        # The initClasses for this are already taken care of by python-for-android
        android_bindings_jar = jars_dir / "Qt6AndroidBindings.jar"
        if android_bindings_jar.exists():
            jars.add(str(android_bindings_jar))
        else:
            raise FileNotFoundError(f"{android_bindings_jar} not found in wheel")

        return jars, init_classes


class Buildozer:
    dry_run = False

    @staticmethod
    def initialize(pysidedeploy_config: AndroidConfig):
        project_dir = Path(pysidedeploy_config.project_dir)
        buildozer_spec = project_dir / "buildozer.spec"
        if buildozer_spec.exists():
            logging.warning(f"[DEPLOY] buildozer.spec already present in {str(project_dir)}."
                            "Using it")
            return

        # creates buildozer.spec config file
        command = [sys.executable, "-m", "buildozer", "init"]
        run_command(command=command, dry_run=Buildozer.dry_run)
        if not Buildozer.dry_run:
            if not buildozer_spec.exists():
                raise RuntimeError(f"buildozer.spec not found in {Path.cwd()}")
            BuildozerConfig(buildozer_spec, pysidedeploy_config)

    @staticmethod
    def create_executable(mode: str):
        command = [sys.executable, "-m", "buildozer", "android", mode]
        run_command(command=command, dry_run=Buildozer.dry_run)
