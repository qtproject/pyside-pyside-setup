# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PYSIDE_SETUP_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PYSIDE_SETUP_ROOT))
from build_scripts.utils import (configure_cmake_project,           # noqa: E402
                                 parse_cmake_project_message_info)


PYTHON_VERSION = "3.15"       # major.minor -- used for stdlib paths (lib/pythonX.Y)

TEMPLATES_PATH = Path(__file__).parent / "templates"
IOS_CACHE_DIR = Path.home() / ".pyside6_ios"

DEFAULT_QT_CMAKEDIR = "lib/cmake"
TARGET_QT_INFO_DIR = PYSIDE_SETUP_ROOT / "sources" / "shiboken6" / "config.tests" / "target_qt_info"


def _query_qt_install_cmakedir(
        qt_ios: Path,
        cmake: str = "cmake",
        dry_run: bool = False,
) -> str | None:
    """Query Qt's QT_INSTALL_CMAKEDIR via the target_qt_info config.tests,
    instead of assuming the default 'lib/cmake'."""
    if dry_run:
        print(f"{cmake} -G Ninja -S {TARGET_QT_INFO_DIR} -B <build_dir> "
              f"-DQFP_QT_TARGET_PATH={qt_ios} -DCMAKE_SYSTEM_NAME=iOS")
        return None
    cmake_cache_args = [
        ("QFP_QT_TARGET_PATH", qt_ios),
        ("CMAKE_SYSTEM_NAME", "iOS"),
    ]
    output = configure_cmake_project(
        TARGET_QT_INFO_DIR, cmake,
        temp_prefix_build_path=IOS_CACHE_DIR / "config.tests",
        cmake_cache_args=cmake_cache_args)
    return parse_cmake_project_message_info(output)["qt_info"]["QT_INSTALL_CMAKEDIR"] or None


def python_xcframework_slice_dir(arch: str, simulator: bool) -> str:
    """The simulator slice is always a single merged 'ios-arm64_x86_64-simulator'"""
    return "ios-arm64_x86_64-simulator" if simulator else f"ios-{arch}"


def generate_toolchain(
        arch: str,
        simulator: bool,
        python_xcframework: Path,
        qt_ios: Path,
        dry_run: bool = False,
) -> Path:

    try:
        qt_install_prefix_cmakedir = _query_qt_install_cmakedir(qt_ios, dry_run=dry_run)
    except (RuntimeError, OSError) as e:
        logging.warning(
            f"Failed to find Qt's cmake dir; "
            f"falling back to '{DEFAULT_QT_CMAKEDIR}'.\n{e}"
        )
        qt_install_prefix_cmakedir = None
    qt_cmake_dir = qt_install_prefix_cmakedir or f"{qt_ios}/{DEFAULT_QT_CMAKEDIR}"

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_PATH)))
    template = env.get_template("toolchain_ios.tmpl.cmake")

    content = template.render(
        arch=arch,
        simulator=simulator,
        python_xcframework=str(python_xcframework),
        python_slice_dir=python_xcframework_slice_dir(arch, simulator),
        python_version=PYTHON_VERSION,
        host_python=sys.executable,
        qt_cmake_dir=qt_cmake_dir,
    )

    suffix = f"{arch}_simulator" if simulator else arch
    toolchain_path = IOS_CACHE_DIR / f"toolchain_ios_{suffix}.cmake"
    if dry_run:
        print(f"write toolchain -> {toolchain_path}")
    else:
        IOS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        toolchain_path.write_text(content)
        logging.info(f"Toolchain written: {toolchain_path}")
    return toolchain_path
