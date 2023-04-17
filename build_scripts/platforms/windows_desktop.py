# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import functools
import os
import tempfile

from pathlib import Path

from ..log import log
from ..config import config
from ..options import OPTION
from ..utils import (copydir, copyfile, copy_qt_metatypes,
                     download_and_extract_7z, filter_match, makefile)
from .. import PYSIDE, SHIBOKEN, PYSIDE_WINDOWS_BIN_TOOLS


def prepare_packages_win32(pyside_build, _vars):
    # For now, debug symbols will not be shipped into the package.
    copy_pdbs = False
    pdbs = []
    if (pyside_build.debug or pyside_build.build_type == 'RelWithDebInfo') and copy_pdbs:
        pdbs = ['*.pdb']

    destination_dir = Path("{st_build_dir}/{st_package_name}".format(**_vars))
    destination_qt_dir = destination_dir
    log.info("Copying files...")

    # <install>/lib/site-packages/{st_package_name}/* ->
    # <setup>/{st_package_name}
    # This copies the module .pyd files and various .py files
    # (__init__, config, git version, etc.)
    copydir(
        "{site_packages_dir}/{st_package_name}", destination_dir,
        _vars=_vars)

    if config.is_internal_shiboken_module_build():
        # <build>/shiboken6/doc/html/* ->
        #   <setup>/{st_package_name}/docs/shiboken6
        copydir(
            f"{{build_dir}}/{SHIBOKEN}/doc/html",
            f"{{st_build_dir}}/{{st_package_name}}/docs/{SHIBOKEN}",
            force=False, _vars=_vars)

        # <install>/bin/*.dll -> {st_package_name}/
        copydir(
            "{install_dir}/bin/", destination_qt_dir,
            _filter=["shiboken*.dll"],
            recursive=False, _vars=_vars)

        # <install>/lib/*.lib -> {st_package_name}/
        copydir(
            "{install_dir}/lib/", destination_qt_dir,
            _filter=["shiboken*.lib"],
            recursive=False, _vars=_vars)

        # @TODO: Fix this .pdb file not to overwrite release
        # {shibokengenerator}.pdb file.
        # Task-number: PYSIDE-615
        copydir(
            f"{{build_dir}}/{SHIBOKEN}/shibokenmodule", destination_dir,
            _filter=pdbs,
            recursive=False, _vars=_vars)

        # pdb files for libshiboken and libpyside
        copydir(
            f"{{build_dir}}/{SHIBOKEN}/libshiboken", destination_dir,
            _filter=pdbs,
            recursive=False, _vars=_vars)

    if config.is_internal_shiboken_generator_build():
        # <install>/bin/*.dll -> {st_package_name}/
        copydir(
            "{install_dir}/bin/", destination_dir,
            _filter=["shiboken*.exe"],
            recursive=False, _vars=_vars)

        # Used to create scripts directory.
        makefile(f"{destination_dir}/scripts/shiboken_tool.py", _vars=_vars)

        # For setting up setuptools entry points.
        copyfile(
            "{install_dir}/bin/shiboken_tool.py",
            f"{destination_dir}/scripts/shiboken_tool.py",
            force=False, _vars=_vars)

        # @TODO: Fix this .pdb file not to overwrite release
        # {shibokenmodule}.pdb file.
        # Task-number: PYSIDE-615
        copydir(
            f"{{build_dir}}/{SHIBOKEN}/generator", destination_dir,
            _filter=pdbs,
            recursive=False, _vars=_vars)

    if config.is_internal_shiboken_generator_build() or config.is_internal_pyside_build():
        # <install>/include/* -> <setup>/{st_package_name}/include
        copydir(
            "{install_dir}/include/{cmake_package_name}",
            destination_dir / "include",
            _vars=_vars)

    if config.is_internal_pyside_build():
        # <build>/pyside6/{st_package_name}/*.pdb ->
        # <setup>/{st_package_name}
        copydir(
            f"{{build_dir}}/{PYSIDE}/{{st_package_name}}", destination_dir,
            _filter=pdbs,
            recursive=False, _vars=_vars)

        makefile(f"{destination_dir}/scripts/__init__.py", _vars=_vars)

        # For setting up setuptools entry points
        for script in ("pyside_tool.py", "metaobjectdump.py", "project.py", "qml.py",
                       "qtpy2cpp.py", "deploy.py"):
            src = f"{{install_dir}}/bin/{script}"
            target = f"{{st_build_dir}}/{{st_package_name}}/scripts/{script}"
            copyfile(src, target, force=False, _vars=_vars)

        for script_dir in ("qtpy2cpp_lib", "deploy_lib", "project"):
            src = f"{{install_dir}}/bin/{script_dir}"
            target = f"{{st_build_dir}}/{{st_package_name}}/scripts/{script_dir}"
            # Exclude subdirectory tests
            copydir(src, target, _filter=["*.py", "*.spec"], recursive=False, _vars=_vars)

        # <install>/bin/*.exe,*.dll -> {st_package_name}/
        filters = ["pyside*.exe", "pyside*.dll"]
        if not OPTION['NO_QT_TOOLS']:
            filters.extend([f"{tool}.exe" for tool in PYSIDE_WINDOWS_BIN_TOOLS])
        copydir("{install_dir}/bin/", destination_qt_dir,
                _filter=filters,
                recursive=False, _vars=_vars)

        copy_qt_metatypes(destination_qt_dir, _vars)

        # <install>/lib/*.lib -> {st_package_name}/
        copydir(
            "{install_dir}/lib/", destination_dir,
            _filter=["pyside*.lib"],
            recursive=False, _vars=_vars)

        copydir("{qt_module_json_files_dir}",
                destination_qt_dir / "modules",
                _filter=["*.json"], _vars=_vars)

        # <install>/share/{st_package_name}/typesystems/* ->
        #   <setup>/{st_package_name}/typesystems
        copydir(
            "{install_dir}/share/{st_package_name}/typesystems",
            destination_dir / "typesystems",
            _vars=_vars)

        # <install>/share/{st_package_name}/glue/* ->
        #   <setup>/{st_package_name}/glue
        copydir(
            "{install_dir}/share/{st_package_name}/glue",
            destination_dir / "glue",
            _vars=_vars)

        # <source>/pyside6/{st_package_name}/support/* ->
        #   <setup>/{st_package_name}/support/*
        copydir(
            f"{{build_dir}}/{PYSIDE}/{{st_package_name}}/support",
            destination_dir / "support",
            _vars=_vars)

        # <source>/pyside6/{st_package_name}/*.pyi ->
        #   <setup>/{st_package_name}/*.pyi
        copydir(
            f"{{build_dir}}/{PYSIDE}/{{st_package_name}}", destination_dir,
            _filter=["*.pyi", "py.typed"],
            _vars=_vars)

        copydir(
            f"{{build_dir}}/{PYSIDE}/libpyside", destination_dir,
            _filter=pdbs,
            recursive=False, _vars=_vars)

        if _vars['ssl_libs_dir']:
            # <ssl_libs>/* -> <setup>/{st_package_name}/openssl
            copydir("{ssl_libs_dir}", destination_dir / "openssl",
                    _filter=[
                        "libeay32.dll",
                        "ssleay32.dll"],
                    force=False, _vars=_vars)

    if config.is_internal_shiboken_module_build():
        # The C++ std library dlls need to be packaged with the
        # shiboken module, because libshiboken uses C++ code.
        copy_msvc_redist_files(destination_dir)

    if config.is_internal_pyside_build() or config.is_internal_shiboken_generator_build():
        copy_qt_artifacts(pyside_build, destination_qt_dir, copy_pdbs, _vars)
        copy_msvc_redist_files(destination_dir)


# MSVC redistributable file list.
msvc_redist = [
    "concrt140.dll",
    "msvcp140.dll",
    "vcamp140.dll",
    "vccorlib140.dll",
    "vcomp140.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "msvcp140_1.dll",
    "msvcp140_2.dll",
    "msvcp140_codecvt_ids.dll"
]


def copy_msvc_redist_files(destination_dir):
    in_coin = os.environ.get('COIN_LAUNCH_PARAMETERS', None)
    if in_coin is None:
        log.info("Qt dependency DLLs (MSVC redist) will not be copied.")
        return

    # Make a directory where the files should be extracted.
    if not destination_dir.exists():
        destination_dir.mkdir(parents=True)

    # Copy Qt dependency DLLs (MSVC) from PATH when building on Qt CI.
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        try:
            for f in Path(path).glob("*140*.dll"):
                if f.name in msvc_redist:
                    copyfile(f, Path(destination_dir) / f.name)
                    msvc_redist.remove(f.name)
            if not msvc_redist:
                break
        except WindowsError:
            continue

    if msvc_redist:
        msg = "The following Qt dependency DLLs (MSVC redist) were not found: {msvc_redist}"
        raise FileNotFoundError(msg)


def copy_qt_dependency_dlls(_vars, destination_qt_dir, artifacts):
    # Extract Qt dependency dlls when building on Qt CI.
    in_coin = os.environ.get('COIN_LAUNCH_PARAMETERS', None)
    if in_coin is None:
        log.info("Qt dependency DLLs will not be downloaded and extracted.")
        return

    with tempfile.TemporaryDirectory() as temp_path:
        redist_url = "https://download.qt.io/development_releases/prebuilt/vcredist/"
        zip_file = "pyside_qt_deps_64_2019.7z"
        if "{target_arch}".format(**_vars) == "32":
            zip_file = "pyside_qt_deps_32_2019.7z"
        try:
            download_and_extract_7z(redist_url + zip_file, temp_path)
        except Exception as e:
            log.warning(f"Download failed: {type(e).__name__}: {e}")
            log.warning("download.qt.io is down, try with mirror")
            redist_url = "https://master.qt.io/development_releases/prebuilt/vcredist/"
            download_and_extract_7z(redist_url + zip_file, temp_path)
        copydir(temp_path, destination_qt_dir, _filter=artifacts, recursive=False, _vars=_vars)


def copy_qt_artifacts(pyside_build, destination_qt_dir, copy_pdbs, _vars):
    built_modules = pyside_build.get_built_pyside_config(_vars)['built_modules']

    constrain_modules = None
    copy_plugins = True
    copy_qml = True
    copy_translations = True
    copy_qt_conf = True
    copy_qt_permanent_artifacts = True
    copy_clang = False

    if config.is_internal_shiboken_generator_build():
        constrain_modules = ["Core", "Network", "Xml", "XmlPatterns"]
        copy_plugins = False
        copy_qml = False
        copy_translations = False
        copy_qt_conf = False
        copy_qt_permanent_artifacts = False
        copy_clang = True

    # <qt>/bin/*.dll and Qt *.exe -> <setup>/{st_package_name}
    qt_artifacts_permanent = [
        "opengl*.dll",
        "designer.exe",
        "linguist.exe",
        "lrelease.exe",
        "lupdate.exe",
        "lconvert.exe",
        "qtdiag.exe"
    ]

    # Choose which EGL library variants to copy.
    qt_artifacts_egl = [
        "libEGL{}.dll",
        "libGLESv2{}.dll"
    ]
    if pyside_build.qtinfo.build_type != 'debug_and_release':
        egl_suffix = '*'
    elif pyside_build.debug:
        egl_suffix = 'd'
    else:
        egl_suffix = ''
    qt_artifacts_egl = [a.format(egl_suffix) for a in qt_artifacts_egl]

    if copy_qt_permanent_artifacts:
        artifacts = qt_artifacts_permanent + qt_artifacts_egl
        copy_qt_dependency_dlls(_vars, destination_qt_dir, artifacts)

    # <qt>/bin/*.dll and Qt *.pdbs -> <setup>/{st_package_name} part two
    # File filter to copy only debug or only release files.
    if constrain_modules:
        qt_dll_patterns = [f"Qt6{x}{{}}.dll" for x in constrain_modules]
        if copy_pdbs:
            qt_dll_patterns += [f"Qt6{x}{{}}.pdb" for x in constrain_modules]
    else:
        qt_dll_patterns = ["Qt6*{}.dll", "lib*{}.dll"]
        if copy_pdbs:
            qt_dll_patterns += ["Qt6*{}.pdb", "lib*{}.pdb"]

    def qt_build_config_filter(patterns, file_name, file_full_path):
        release = [a.format('') for a in patterns]
        debug = [a.format('d') for a in patterns]

        # If qt is not a debug_and_release build, that means there
        # is only one set of shared libraries, so we can just copy
        # them.
        if pyside_build.qtinfo.build_type != 'debug_and_release':
            if filter_match(file_name, release):
                return True
            return False

        # Setup Paths
        file_name = Path(file_name)
        file_full_path = Path(file_full_path)

        # In debug_and_release case, choosing which files to copy
        # is more difficult. We want to copy only the files that
        # match the PySide6 build type. So if PySide6 is built in
        # debug mode, we want to copy only Qt debug libraries
        # (ending with "d.dll"). Or vice versa. The problem is that
        # some libraries have "d" as the last character of the
        # actual library name (for example Qt6Gamepad.dll and
        # Qt6Gamepadd.dll). So we can't just match a pattern ending
        # in "d". Instead we check if there exists a file with the
        # same name plus an additional "d" at the end, and using
        # that information we can judge if the currently processed
        # file is a debug or release file.

        # e.g. ["Qt6Cored", ".dll"]
        file_base_name = file_name.stem
        file_ext = file_name.suffix
        # e.g. "/home/work/qt/qtbase/bin"
        file_path_dir_name = file_full_path.parent
        # e.g. "Qt6Coredd"
        maybe_debug_name = f"{file_base_name}d"
        if pyside_build.debug:
            _filter = debug

            def predicate(path):
                return not path.exists()
        else:
            _filter = release

            def predicate(path):
                return path.exists()
        # e.g. "/home/work/qt/qtbase/bin/Qt6Coredd.dll"
        other_config_path = file_path_dir_name / (maybe_debug_name + file_ext)

        if (filter_match(file_name, _filter) and predicate(other_config_path)):
            return True
        return False

    qt_dll_filter = functools.partial(qt_build_config_filter,
                                      qt_dll_patterns)
    copydir("{qt_bin_dir}", destination_qt_dir,
            file_filter_function=qt_dll_filter,
            recursive=False, _vars=_vars)

    if copy_plugins:
        is_pypy = "pypy" in pyside_build.build_classifiers
        # <qt>/plugins/* -> <setup>/{st_package_name}/plugins
        plugins_target = f"{destination_qt_dir}/plugins"
        plugin_dll_patterns = ["*{}.dll"]
        pdb_pattern = "*{}.pdb"
        if copy_pdbs:
            plugin_dll_patterns += [pdb_pattern]
        plugin_dll_filter = functools.partial(qt_build_config_filter, plugin_dll_patterns)
        copydir("{qt_plugins_dir}", plugins_target,
                file_filter_function=plugin_dll_filter,
                _vars=_vars)
        if not is_pypy:
            copydir("{install_dir}/plugins/designer",
                    f"{plugins_target}/designer",
                    _filter=["*.dll"],
                    recursive=False,
                    _vars=_vars)

    if copy_translations:
        # <qt>/translations/* -> <setup>/{st_package_name}/translations
        copydir("{qt_translations_dir}", f"{destination_qt_dir}/translations",
                _filter=["*.qm", "*.pak"],
                force=False,
                _vars=_vars)

    if copy_qml:
        # <qt>/qml/* -> <setup>/{st_package_name}/qml
        qml_dll_patterns = ["*{}.dll"]
        qml_ignore_patterns = qml_dll_patterns + [pdb_pattern]
        qml_ignore = [a.format('') for a in qml_ignore_patterns]

        # Copy all files that are not dlls and pdbs (.qml, qmldir).
        copydir("{qt_qml_dir}", f"{destination_qt_dir}/qml",
                ignore=qml_ignore,
                force=False,
                recursive=True,
                _vars=_vars)

        if copy_pdbs:
            qml_dll_patterns += [pdb_pattern]
        qml_dll_filter = functools.partial(qt_build_config_filter, qml_dll_patterns)

        # Copy all dlls (and possibly pdbs).
        copydir("{qt_qml_dir}", f"{destination_qt_dir}/qml",
                file_filter_function=qml_dll_filter,
                force=False,
                recursive=True,
                _vars=_vars)

    if pyside_build.is_webengine_built(built_modules):
        copydir("{qt_data_dir}/resources", f"{destination_qt_dir}/resources",
                _filter=None,
                recursive=False,
                _vars=_vars)

        _ext = "d" if pyside_build.debug else ""
        _filter = [f"QtWebEngineProcess{_ext}.exe"]
        copydir("{qt_bin_dir}", destination_qt_dir,
                _filter=_filter,
                recursive=False, _vars=_vars)

    if copy_qt_conf:
        # Copy the qt.conf file to prefix dir.
        copyfile(f"{{build_dir}}/{PYSIDE}/{{st_package_name}}/qt.conf",
                 destination_qt_dir,
                 _vars=_vars)

    if copy_clang:
        pyside_build.prepare_standalone_clang(is_win=True)
