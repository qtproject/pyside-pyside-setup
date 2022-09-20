# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os

from ..config import config
from ..options import OPTION
from ..utils import (copy_icu_libs, copydir, copyfile, find_files_using_glob,
                     linux_patch_executable)
from ..versions import PYSIDE


def prepare_standalone_package_linux(self, _vars):
    built_modules = _vars['built_modules']

    constrain_modules = None
    copy_plugins = True
    copy_qml = True
    copy_translations = True
    copy_qt_conf = True
    should_copy_icu_libs = True

    if config.is_internal_shiboken_generator_build():
        constrain_modules = ["Core", "Network", "Xml", "XmlPatterns"]
        copy_plugins = False
        copy_qml = False
        copy_translations = False
        copy_qt_conf = False
        should_copy_icu_libs = False

    # <qt>/lib/* -> <setup>/{st_package_name}/Qt/lib
    destination_lib_dir = "{st_build_dir}/{st_package_name}/Qt/lib"

    accepted_modules = ['libQt6*.so.?']
    if constrain_modules:
        accepted_modules = [f"libQt6{module}*.so.?" for module in constrain_modules]
    accepted_modules.append("libicu*.so.??")

    copydir("{qt_lib_dir}", destination_lib_dir,
            _filter=accepted_modules,
            recursive=False, _vars=_vars, force_copy_symlinks=True)

    if should_copy_icu_libs:
        # Check if ICU libraries were copied over to the destination
        # Qt libdir.
        resolved_destination_lib_dir = destination_lib_dir.format(**_vars)
        maybe_icu_libs = find_files_using_glob(resolved_destination_lib_dir, "libicu*")

        # If no ICU libraries are present in the Qt libdir (like when
        # Qt is built against system ICU, or in the Coin CI where ICU
        # libs are in a different directory) try to find out / resolve
        # which ICU libs are used by QtCore (if used at all) using a
        # custom written ldd, and copy the ICU libs to the Pyside Qt
        # dir if necessary. We choose the QtCore lib to inspect, by
        # checking which QtCore library the shiboken6 executable uses.
        if not maybe_icu_libs:
            copy_icu_libs(self._patchelf_path, resolved_destination_lib_dir)

    # Set RPATH for Qt libs.
    self.update_rpath_for_linux_qt_libraries(destination_lib_dir.format(**_vars))

    # Patching designer to use the Qt libraries provided in the wheel
    if config.is_internal_pyside_build() and not OPTION['NO_QT_TOOLS']:
        assistant_path = "{st_build_dir}/{st_package_name}/assistant".format(**_vars)
        linux_patch_executable(self._patchelf_path, assistant_path)
        designer_path = "{st_build_dir}/{st_package_name}/designer".format(**_vars)
        linux_patch_executable(self._patchelf_path, designer_path)

    if self.is_webengine_built(built_modules):
        copydir("{qt_data_dir}/resources",
                "{st_build_dir}/{st_package_name}/Qt/resources",
                _filter=None,
                recursive=False,
                _vars=_vars)

    if copy_plugins:
        is_pypy = "pypy" in self.build_classifiers
        # <qt>/plugins/* -> <setup>/{st_package_name}/Qt/plugins
        plugins_target = "{st_build_dir}/{st_package_name}/Qt/plugins"
        copydir("{qt_plugins_dir}", plugins_target,
                _filter=["*.so"],
                recursive=True,
                _vars=_vars)
        if not is_pypy:
            copydir("{install_dir}/plugins/designer",
                    f"{plugins_target}/designer",
                    _filter=["*.so"],
                    recursive=False,
                    _vars=_vars)

        copied_plugins = self.get_shared_libraries_in_path_recursively(
            plugins_target.format(**_vars))
        self.update_rpath_for_linux_plugins(copied_plugins)

    if copy_qml:
        # <qt>/qml/* -> <setup>/{st_package_name}/Qt/qml
        qml_plugins_target = "{st_build_dir}/{st_package_name}/Qt/qml"
        copydir("{qt_qml_dir}",
                qml_plugins_target,
                _filter=None,
                force=False,
                recursive=True,
                ignore=["*.debug"],
                _vars=_vars)
        copied_plugins = self.get_shared_libraries_in_path_recursively(
            qml_plugins_target.format(**_vars))
        self.update_rpath_for_linux_plugins(
            copied_plugins,
            qt_lib_dir=destination_lib_dir.format(**_vars),
            is_qml_plugin=True)

    if copy_translations:
        # <qt>/translations/* ->
        # <setup>/{st_package_name}/Qt/translations
        copydir("{qt_translations_dir}",
                "{st_build_dir}/{st_package_name}/Qt/translations",
                _filter=["*.qm", "*.pak"],
                force=False,
                _vars=_vars)

    if copy_qt_conf:
        # Copy the qt.conf file to libexec.
        qt_libexec_path = "{st_build_dir}/{st_package_name}/Qt/libexec".format(**_vars)
        if not os.path.isdir(qt_libexec_path):
            os.makedirs(qt_libexec_path)
        copyfile(f"{{build_dir}}/{PYSIDE}/{{st_package_name}}/qt.conf",
                 qt_libexec_path, _vars=_vars)
