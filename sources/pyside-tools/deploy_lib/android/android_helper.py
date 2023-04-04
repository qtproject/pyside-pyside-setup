# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from zipfile import ZipFile
from dataclasses import dataclass


@dataclass
class AndroidData:
    wheel_pyside: Path
    wheel_shiboken: Path
    ndk_path: Path
    sdk_path: Path


def create_recipe(version: str, component: str, wheel_path: str, generated_files_path: Path):
    '''
    Create python_for_android recipe for PySide6 and shiboken6
    '''
    rcp_tmpl_path = Path(__file__).parent / "recipes" / f"{component}"
    environment = Environment(loader=FileSystemLoader(rcp_tmpl_path))
    template = environment.get_template("__init__.tmpl.py")
    content = template.render(
        version=version,
        wheel_path=wheel_path,
    )

    recipe_path = generated_files_path / "recipes" / f"{component}"
    recipe_path.mkdir(parents=True, exist_ok=True)
    logging.info(f"[DEPLOY] Writing {component} recipe into {recipe_path}")
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
    return jar_path


def get_wheel_android_arch(wheel: Path):
    '''
    Get android architecture from wheel
    '''
    supported_archs = ["aarch64", "armv7a", "i686", "x86_64"]
    for arch in supported_archs:
        if arch in wheel.stem:
            return arch

    return None
