# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
from pathlib import Path

from ..log import log
from ..config import config
from ..options import OPTION
from ..utils import copydir, copyfile, copy_qt_metatypes, makefile
from .. import PYSIDE, SHIBOKEN
from .linux import prepare_standalone_package_linux
from .macos import prepare_standalone_package_macos


def _macos_copy_gui_executable(name, _vars=None):
    """macOS helper: Copy a GUI executable from the .app folder and return the
       files"""
    app_name = f"{name.capitalize()}.app"
    return copydir(f"{{install_dir}}/bin/{app_name}",
                   f"{{st_build_dir}}/{{st_package_name}}/{app_name}",
                   _filter=None, recursive=True,
                   force=False, _vars=_vars)


def _unix_copy_gui_executable(name, _vars=None):
    """UNIX helper: Copy a GUI executable and return the files"""
    return copydir("{install_dir}/bin/",
                   "{st_build_dir}/{st_package_name}/",
                   _filter=[name],
                   force=False, _vars=_vars)


def _copy_gui_executable(name, _vars=None):
    """Copy a GUI executable and return the files"""
    if sys.platform == 'darwin':
        return _macos_copy_gui_executable(name, _vars)
    return _unix_copy_gui_executable(name, _vars)


def prepare_packages_posix(pyside_build, _vars, cross_build=False):
    is_android = False
    if str(OPTION['PLAT_NAME']).startswith('android'):
        is_android = True

    executables = []
    libexec_executables = []
    log.info("Copying files...")

    destination_dir = Path("{st_build_dir}/{st_package_name}".format(**_vars))
    destination_qt_dir = destination_dir / "Qt"

    # <install>/lib/site-packages/{st_package_name}/* ->
    # <setup>/{st_package_name}
    # This copies the module .so/.dylib files and various .py files
    # (__init__, config, git version, etc.)
    copydir(
        "{site_packages_dir}/{st_package_name}", destination_dir,
        _vars=_vars)

    generated_config = pyside_build.get_built_pyside_config(_vars)

    def adjusted_lib_name(name, version):
        postfix = ''
        if config.is_cross_compile() and is_android:
            postfix = ".so"
        elif sys.platform.startswith('linux'):
            postfix = f".so.{version}"
        elif sys.platform == 'darwin':
            postfix = f".{version}.dylib"
        return name + postfix

    if config.is_internal_shiboken_module_build():
        # <build>/shiboken6/doc/html/* ->
        #   <setup>/{st_package_name}/docs/shiboken6
        copydir(
            f"{{build_dir}}/{SHIBOKEN}/doc/html",
            f"{{st_build_dir}}/{{st_package_name}}/docs/{SHIBOKEN}",
            force=False, _vars=_vars)

        # <install>/lib/lib* -> {st_package_name}/
        copydir(
            "{install_dir}/lib/", destination_dir,
            _filter=[
                adjusted_lib_name("libshiboken*",
                                  generated_config['shiboken_library_soversion']),
            ],
            recursive=False, _vars=_vars, force_copy_symlinks=True)

    if config.is_internal_shiboken_generator_build():
        # <install>/bin/* -> {st_package_name}/
        executables.extend(copydir(
            "{install_dir}/bin/", destination_dir,
            _filter=[SHIBOKEN],
            recursive=False, _vars=_vars))

        # Used to create scripts directory.
        makefile(
            "{st_build_dir}/{st_package_name}/scripts/shiboken_tool.py",
            _vars=_vars)

        # For setting up setuptools entry points.
        copyfile(
            "{install_dir}/bin/shiboken_tool.py",
            "{st_build_dir}/{st_package_name}/scripts/shiboken_tool.py",
            force=False, _vars=_vars)

    if config.is_internal_shiboken_generator_build() or config.is_internal_pyside_build():
        # <install>/include/* -> <setup>/{st_package_name}/include
        copydir(
            "{install_dir}/include/{cmake_package_name}",
            "{st_build_dir}/{st_package_name}/include",
            _vars=_vars)

    if config.is_internal_pyside_build():
        if not is_android:
            makefile(
                "{st_build_dir}/{st_package_name}/scripts/__init__.py",
                _vars=_vars)

            scripts = ["pyside_tool.py", "metaobjectdump.py", "project.py", "qml.py",
                       "qtpy2cpp.py", "deploy.py"]

            script_dirs = ["qtpy2cpp_lib", "deploy_lib",  "project"]

            if sys.platform.startswith("linux"):
                scripts.append("android_deploy.py")
                script_dirs.extend(["deploy_lib/android",
                                    "deploy_lib/android/recipes/PySide6",
                                    "deploy_lib/android/recipes/shiboken6",])

            # For setting up setuptools entry points
            for script in scripts:
                src = f"{{install_dir}}/bin/{script}"
                target = f"{{st_build_dir}}/{{st_package_name}}/scripts/{script}"
                copyfile(src, target, force=False, _vars=_vars)

            for script_dir in script_dirs:
                src = f"{{install_dir}}/bin/{script_dir}"
                target = f"{{st_build_dir}}/{{st_package_name}}/scripts/{script_dir}"
                # Exclude subdirectory tests
                copydir(src, target, _filter=["*.py", "*.spec", "*.jpg"], recursive=False, _vars=_vars)

            # <install>/bin/* -> {st_package_name}/
            executables.extend(copydir(
                "{install_dir}/bin/", destination_dir,
                _filter=[f"{PYSIDE}-lupdate"],
                recursive=False, _vars=_vars))

            lib_exec_filters = []
            if not OPTION['NO_QT_TOOLS']:
                lib_exec_filters.extend(['uic', 'rcc', 'qmltyperegistrar', 'qmlimportscanner'])
                executables.extend(copydir(
                    "{install_dir}/bin/", destination_dir,
                    _filter=["lrelease", "lupdate", "qmllint", "qmlformat", "qmlls"],
                    recursive=False, _vars=_vars))
                # Copying assistant/designer
                executables.extend(_copy_gui_executable('assistant', _vars=_vars))
                executables.extend(_copy_gui_executable('designer', _vars=_vars))
                executables.extend(_copy_gui_executable('linguist', _vars=_vars))

            copy_qt_metatypes(destination_qt_dir, _vars)

            # Copy libexec
            built_modules = pyside_build.get_built_pyside_config(_vars)['built_modules']
            if pyside_build.is_webengine_built(built_modules):
                lib_exec_filters.append('QtWebEngineProcess')
            if lib_exec_filters:
                libexec_executables.extend(copydir("{qt_lib_execs_dir}",
                                                destination_qt_dir / "libexec",
                                                _filter=lib_exec_filters,
                                                recursive=False,
                                                _vars=_vars))

        # <install>/lib/lib* -> {st_package_name}/
        copydir(
            "{install_dir}/lib", destination_dir,
            _filter=[
                adjusted_lib_name("libpyside*",
                                  generated_config['pyside_library_soversion']),
            ],
            recursive=False, _vars=_vars, force_copy_symlinks=True)

        if not config.is_cross_compile():
            # <install>/share/{st_package_name}/typesystems/* ->
            #   <setup>/{st_package_name}/typesystems
            copydir(
                "{install_dir}/share/{st_package_name}/typesystems",
                "{st_build_dir}/{st_package_name}/typesystems",
                _vars=_vars)

            # <install>/share/{st_package_name}/glue/* ->
            #   <setup>/{st_package_name}/glue
            copydir(
                "{install_dir}/share/{st_package_name}/glue",
                "{st_build_dir}/{st_package_name}/glue",
                _vars=_vars)

        if not is_android:
            # <source>/pyside6/{st_package_name}/support/* ->
            #   <setup>/{st_package_name}/support/*
            copydir(
                f"{{build_dir}}/{PYSIDE}/{{st_package_name}}/support",
                "{st_build_dir}/{st_package_name}/support",
                _vars=_vars)

        # <source>/pyside6/{st_package_name}/*.pyi ->
        #   <setup>/{st_package_name}/*.pyi
        copydir(
            f"{{build_dir}}/{PYSIDE}/{{st_package_name}}", destination_dir,
            _filter=["*.pyi", "py.typed"],
            _vars=_vars)

        # copy the jar files
        if is_android:
            copydir(
                "{install_dir}/lib/jar",
                "{st_build_dir}/{st_package_name}/jar",
                _vars=_vars)

    # Copy Qt libs to package
    if OPTION["STANDALONE"]:
        if config.is_internal_pyside_build() or config.is_internal_shiboken_generator_build():
            _vars['built_modules'] = generated_config['built_modules']
            if sys.platform == 'darwin':
                prepare_standalone_package_macos(pyside_build, _vars)
            else:
                prepare_standalone_package_linux(pyside_build, _vars, cross_build,
                                                 is_android=is_android)

        if config.is_internal_shiboken_generator_build():
            # Copy over clang before rpath patching.
            pyside_build.prepare_standalone_clang(is_win=False)

    # Update rpath to $ORIGIN
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        rpath_path = destination_dir
        pyside_build.update_rpath(rpath_path, executables)
        pyside_build.update_rpath(rpath_path, pyside_build.package_libraries(rpath_path))
        if libexec_executables:
            pyside_build.update_rpath(rpath_path, libexec_executables, libexec=True)
