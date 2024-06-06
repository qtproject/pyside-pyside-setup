# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
import sys
import logging
import zipfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from jinja2 import Environment, FileSystemLoader

from .. import run_command


@dataclass
class AndroidData:
    """
    Dataclass to store all the Android data obtained through cli
    """
    wheel_pyside: Path
    wheel_shiboken: Path
    ndk_path: Path
    sdk_path: Path


def create_recipe(version: str, component: str, wheel_path: str, generated_files_path: Path,
                  qt_modules: list[str] = None, local_libs: list[str] = None,
                  plugins: list[str] = None):
    '''
    Create python_for_android recipe for PySide6 and shiboken6
    '''
    qt_plugins = []
    if plugins:
        # split plugins based on category
        for plugin in plugins:
            plugin_category, plugin_name = plugin.split('_', 1)
            qt_plugins.append((plugin_category, plugin_name))

    qt_local_libs = []
    if local_libs:
        qt_local_libs = [local_lib for local_lib in local_libs if local_lib.startswith("Qt6")]

    rcp_tmpl_path = Path(__file__).parent / "recipes" / f"{component}"
    environment = Environment(loader=FileSystemLoader(rcp_tmpl_path))
    template = environment.get_template("__init__.tmpl.py")
    content = template.render(
        version=version,
        wheel_path=wheel_path,
        qt_modules=qt_modules,
        qt_local_libs=qt_local_libs,
        qt_plugins=qt_plugins
    )

    recipe_path = generated_files_path / "recipes" / f"{component}"
    recipe_path.mkdir(parents=True, exist_ok=True)
    logging.info(f"[DEPLOY] Writing {component} recipe into {str(recipe_path)}")
    with open(recipe_path / "__init__.py", mode="w", encoding="utf-8") as recipe:
        recipe.write(content)


def extract_and_copy_jar(wheel_path: Path, generated_files_path: Path) -> str:
    '''
    extracts the PySide6 wheel and copies the 'jar' folder to 'generated_files_path'.
    These .jar files are added to the buildozer.spec file to be used later by buildozer
    '''
    jar_path = generated_files_path / "jar"
    jar_path.mkdir(parents=True, exist_ok=True)
    archive = ZipFile(wheel_path)
    jar_files = [file for file in archive.namelist() if file.startswith("PySide6/jar")]
    for file in jar_files:
        archive.extract(file, jar_path)
    return (jar_path / "PySide6" / "jar").resolve() if jar_files else None


def get_wheel_android_arch(wheel: Path):
    '''
    Get android architecture from wheel
    '''
    supported_archs = ["aarch64", "armv7a", "i686", "x86_64"]
    for arch in supported_archs:
        if arch in wheel.stem:
            return arch

    return None


def get_llvm_readobj(ndk_path: Path) -> Path:
    '''
    Return the path to llvm_readobj from the Android Ndk
    '''
    # TODO: Requires change if Windows platform supports Android Deployment or if we
    # support host other than linux-x86_64
    return (ndk_path / f"toolchains/llvm/prebuilt/{sys.platform}-x86_64/bin/llvm-readobj")


def find_lib_dependencies(llvm_readobj: Path, lib_path: Path, used_dependencies: set[str] = None,
                          dry_run: bool = False):
    """
    Find all the Qt dependencies of a library using llvm_readobj
    """
    if lib_path.name in used_dependencies:
        return

    used_dependencies.add(lib_path.name)

    command = [str(llvm_readobj), "--needed-libs", str(lib_path)]

    # even if dry_run is given, we need to run the actual command to see all the dependencies
    # for which llvm-readelf is run.
    if dry_run:
        _, output = run_command(command=command, dry_run=dry_run, fetch_output=True)
    _, output = run_command(command=command, dry_run=False, fetch_output=True)

    dependencies = set()
    neededlibraries_found = False
    for line in output.splitlines():
        line = line.decode("utf-8").lstrip()
        if line.startswith("NeededLibraries") and not neededlibraries_found:
            neededlibraries_found = True
        if neededlibraries_found and line.startswith("libQt"):
            dependencies.add(line)
            used_dependencies.add(line)
            dependent_lib_path = lib_path.parent / line
            find_lib_dependencies(llvm_readobj, dependent_lib_path, used_dependencies, dry_run)

    if dependencies:
        logging.info(f"[DEPLOY] Following dependencies found for {lib_path.stem}: {dependencies}")
    else:
        logging.info(f"[DEPLOY] No Qt dependencies found for {lib_path.stem}")


def find_qtlibs_in_wheel(wheel_pyside: Path):
    """
    Find the path to Qt/lib folder inside the wheel.
    """
    archive = ZipFile(wheel_pyside)
    qt_libs_path = wheel_pyside / "PySide6/Qt/lib"
    qt_libs_path = zipfile.Path(archive, at=qt_libs_path)
    if not qt_libs_path.exists():
        for file in archive.namelist():
            # the dependency files are inside the libs folder
            if file.endswith("android-dependencies.xml"):
                qt_libs_path = zipfile.Path(archive, at=file).parent
                # all dependency files are in the same path
                break

    if not qt_libs_path:
        raise FileNotFoundError("[DEPLOY] Unable to find Qt libs folder inside the wheel")

    return qt_libs_path
