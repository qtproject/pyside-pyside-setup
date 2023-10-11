# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import PySide6
from pathlib import Path
from typing import List

from pkginfo import Wheel

from .. import MAJOR_VERSION, BaseConfig, Config, run_command
from . import (create_recipe, find_lib_dependencies, find_qtlibs_in_wheel,
               get_llvm_readobj)

# They all start with `Qt` as the prefix. Removing this prefix and getting the actual
# module name
ALL_PYSIDE_MODULES = [module[2:] for module in PySide6.__all__]


class BuildozerConfig(BaseConfig):
    def __init__(self, buildozer_spec_file: Path, pysidedeploy_config: Config,
                 generated_files_path: Path):
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
        self.set_value("app", "p4a.bootstrap", "qt")

        self.qt_libs_path: zipfile.Path = (
            find_qtlibs_in_wheel(wheel_pyside=pysidedeploy_config.wheel_pyside))
        logging.info(f"[DEPLOY] Found Qt libs path inside wheel: {str(self.qt_libs_path)}")

        extra_modules = self.__find_dependent_qt_modules(pysidedeploy_config)
        logging.info(f"[DEPLOY] Other dependent modules to be added: {extra_modules}")
        pysidedeploy_config.modules = pysidedeploy_config.modules + extra_modules

        # update the config file with the extra modules
        if extra_modules:
            pysidedeploy_config.update_config()

        modules = ",".join(pysidedeploy_config.modules)

        # gets the xml dependency files from Qt installation path
        dependency_files = self.__get_dependency_files(modules=pysidedeploy_config.modules,
                                                       arch=self.arch)

        dependent_plugins = []
        # the local_libs can also store dependent plugins
        local_libs, dependent_plugins = self.__find_local_libs(dependency_files)
        pysidedeploy_config.local_libs += local_libs

        self.__find_plugin_dependencies(dependency_files, dependent_plugins)
        pysidedeploy_config.qt_plugins += dependent_plugins

        if local_libs or dependent_plugins:
            pysidedeploy_config.update_config()

        local_libs = ",".join(pysidedeploy_config.local_libs)

        # create recipes
        # https://python-for-android.readthedocs.io/en/latest/recipes/
        # These recipes are manually added through buildozer.spec file to be used by
        # python_for_android while building the distribution
        if not pysidedeploy_config.recipes_exist() and not pysidedeploy_config.dry_run:
            logging.info("[DEPLOY] Creating p4a recipes for PySide6 and shiboken6")
            version = Wheel(pysidedeploy_config.wheel_pyside).version
            create_recipe(version=version, component=f"PySide{MAJOR_VERSION}",
                          wheel_path=pysidedeploy_config.wheel_pyside,
                          generated_files_path=generated_files_path,
                          qt_modules=pysidedeploy_config.modules,
                          local_libs=pysidedeploy_config.local_libs,
                          plugins=pysidedeploy_config.qt_plugins)
            create_recipe(version=version, component=f"shiboken{MAJOR_VERSION}",
                          wheel_path=pysidedeploy_config.wheel_shiboken,
                          generated_files_path=generated_files_path)
            pysidedeploy_config.recipe_dir = (generated_files_path / "recipes").resolve()
        self.set_value('app', "p4a.local_recipes", str(pysidedeploy_config.recipe_dir))

        # add permissions
        permissions = self.__find_permissions(dependency_files)
        permissions = ", ".join(permissions)
        self.set_value("app", "android.permissions", permissions)

        # add jars and initClasses for the jars
        jars, init_classes = self.__find_jars(dependency_files, pysidedeploy_config.jars_dir)
        self.set_value("app", "android.add_jars", ",".join(jars))
        init_classes = ",".join(init_classes)

        # extra arguments specific to Qt
        extra_args = (f"--qt-libs={modules} --load-local-libs={local_libs}"
                      f" --init-classes={init_classes}")
        self.set_value("app", "p4a.extra_args", extra_args)

        # TODO: does not work atm. Seems like a bug with buildozer
        # change buildozer build_dir
        # self.set_value("buildozer", "build_dir", str(build_dir.relative_to(Path.cwd())))

        # change final apk/aab path
        self.set_value("buildozer", "bin_dir", str(pysidedeploy_config.exe_dir.resolve()))

        self.update_config()

    def __get_dependency_files(self, modules: List[str], arch: str) -> List[zipfile.Path]:
        """
        Based on pysidedeploy_config.modules, returns the
        Qt6{module}_{arch}-android-dependencies.xml file, which contains the various
        dependencies of the module, like permissions, plugins etc
        """
        dependency_files = []
        needed_dependency_files = [(f"Qt{MAJOR_VERSION}{module}_{arch}"
                                    "-android-dependencies.xml") for module in modules]

        for dependency_file_name in needed_dependency_files:
            dependency_file = self.qt_libs_path / dependency_file_name
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

    def __find_jars(self, dependency_files: List[zipfile.Path], jars_dir: Path):
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

    def __find_local_libs(self, dependency_files: List[zipfile.Path]):
        local_libs = set()
        plugins = set()
        lib_pattern = re.compile(f"lib(?P<lib_name>.*)_{self.arch}")
        for dependency_file in dependency_files:
            xml_content = dependency_file.read_text()
            root = ET.fromstring(xml_content)
            for local_lib in root.iter("lib"):

                if 'file' not in local_lib.attrib:
                    if 'name' not in local_lib.attrib:
                        logging.warning("[DEPLOY] Invalid android dependency file"
                                        f" {str(dependency_file)}")
                    continue

                file = local_lib.attrib['file']
                if file.endswith(".so"):
                    # file_name starts with lib and ends with the platform name
                    # eg: lib<lib_name>_x86_64.so
                    file_name = Path(file).stem

                    if file_name.startswith("libplugins_platforms_qtforandroid"):
                        # the platform library is a requisite and is already added from the
                        # configuration file
                        continue

                    # we only need lib_name, because lib and arch gets re-added by
                    # python-for-android
                    match = lib_pattern.search(file_name)
                    if match:
                        lib_name = match.group("lib_name")
                        local_libs.add(lib_name)
                        if lib_name.startswith("plugins"):
                            plugin_name = lib_name.split('plugins_', 1)[1]
                            plugins.add(plugin_name)

        return list(local_libs), list(plugins)

    def __find_plugin_dependencies(self, dependency_files: List[zipfile.Path],
                                   dependent_plugins: List[str]):
        # The `bundled` element in the dependency xml files points to the folder where
        # additional dependencies for the application exists. Inspecting the depenency files
        # in android, this always points to the specific Qt plugin dependency folder.
        # eg: for application using Qt Multimedia, this looks like:
        # <bundled file="./plugins/multimedia" />
        # The code recusively checks all these dependent folders and adds the necessary plugins
        # as dependencies
        lib_pattern = re.compile(f"libplugins_(?P<plugin_name>.*)_{self.arch}.so")
        for dependency_file in dependency_files:
            xml_content = dependency_file.read_text()
            root = ET.fromstring(xml_content)
            for bundled_element in root.iter("bundled"):
                # the attribute 'file' can be misleading, but it always points to the plugin
                # folder on inspecting the dependency files
                if 'file' not in bundled_element.attrib:
                    logging.warning("[DEPLOY] Invalid Android dependency file"
                                    f" {str(dependency_file)}")
                    continue

                # from "./plugins/multimedia" to absolute path in wheel
                plugin_module_folder = bundled_element.attrib['file']
                # they all should start with `./plugins`
                if plugin_module_folder.startswith("./plugins"):
                    plugin_module_folder = plugin_module_folder.partition("./plugins/")[2]
                else:
                    continue

                absolute_plugin_module_folder = (self.qt_libs_path.parent / "plugins" /
                                                plugin_module_folder)

                if not absolute_plugin_module_folder.is_dir():
                    logging.warning(f"[DEPLOY] Qt plugin folder '{plugin_module_folder}' does not"
                                    " exist or is not a directory for this Android platform")
                    continue

                for plugin in absolute_plugin_module_folder.iterdir():
                    plugin_name = plugin.name
                    if plugin_name.endswith(".so") and plugin_name.startswith("libplugins"):
                        # we only need part of plugin_name, because `lib` prefix and `arch` suffix
                        # gets re-added by python-for-android
                        match = lib_pattern.search(plugin_name)
                        if match:
                            plugin_infix_name = match.group("plugin_name")
                            if plugin_infix_name not in dependent_plugins:
                                dependent_plugins.append(plugin_infix_name)

    def __find_dependent_qt_modules(self, pysidedeploy_config: Config):
        """
        Given pysidedeploy_config.modules, find all the other dependent Qt modules. This is
        done by using llvm-readobj (readelf) to find the dependent libraries from the module
        library.
        """
        dependent_modules = set()
        all_dependencies = set()
        lib_pattern = re.compile(f"libQt6(?P<mod_name>.*)_{self.arch}")

        llvm_readobj = get_llvm_readobj(pysidedeploy_config.ndk_path)
        if not llvm_readobj.exists():
            raise FileNotFoundError(f"[DEPLOY] {llvm_readobj} does not exist."
                                    "Finding Qt dependencies failed")

        archive = zipfile.ZipFile(pysidedeploy_config.wheel_pyside)
        lib_path_suffix = Path(str(self.qt_libs_path)).relative_to(pysidedeploy_config.wheel_pyside)

        with tempfile.TemporaryDirectory() as tmpdir:
            archive.extractall(tmpdir)
            qt_libs_tmpdir = Path(tmpdir) / lib_path_suffix
            # find the lib folder where Qt libraries are stored
            for module_name in pysidedeploy_config.modules:
                qt_module_path = qt_libs_tmpdir / f"libQt6{module_name}_{self.arch}.so"
                if not qt_module_path.exists():
                    raise FileNotFoundError(f"[DEPLOY] libQt6{module_name}_{self.arch}.so not found"
                                            " inside the wheel")
                find_lib_dependencies(llvm_readobj=llvm_readobj, lib_path=qt_module_path,
                                      dry_run=pysidedeploy_config.dry_run,
                                      used_dependencies=all_dependencies)

        for dependency in all_dependencies:
            match = lib_pattern.search(dependency)
            if match:
                module = match.group("mod_name")
                if module not in pysidedeploy_config.modules:
                    dependent_modules.add(module)

        # check if the PySide6 binary for the Qt module actually exists
        # eg: libQt6QmlModels.so exists and it includes QML types. Hence, it makes no
        dependent_modules = [module for module in dependent_modules if module in ALL_PYSIDE_MODULES]
        dependent_modules_str = ",".join(dependent_modules)
        logging.info("[DEPLOY] The following extra dependencies were found:"
                     f" {dependent_modules_str}")

        return list(dependent_modules)


class Buildozer:
    dry_run = False

    @staticmethod
    def initialize(pysidedeploy_config: Config, generated_files_path: Path):
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
            BuildozerConfig(buildozer_spec, pysidedeploy_config, generated_files_path)

    @staticmethod
    def create_executable(mode: str):
        command = ["buildozer", "android", mode]
        run_command(command=command, dry_run=Buildozer.dry_run)
