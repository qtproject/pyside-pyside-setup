# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IOSData:
    """Dataclass to store all the iOS data obtained through cli."""
    wheel_pyside: Path
    wheel_shiboken: Path
    xcframework_path: Path


def get_wheel_ios_target(wheel: Path) -> tuple[str, bool] | None:
    """
    Get (arch, simulator) from an iOS wheel's platform tag, e.g.
    '...-ios_arm64.whl' -> ("arm64", False), '...-ios_arm64_simulator.whl' -> ("arm64", True)
    """
    match = re.search(r"ios_(arm64|x86_64)(_simulator)?$", wheel.stem)
    if not match:
        return None
    return match.group(1), match.group(2) is not None


def get_xcframework_python_version(xcframework_path: Path) -> str | None:
    """
    Get the Python version from Python.xcframework
    """
    lib_dir = xcframework_path / "lib"
    if not lib_dir.is_dir():
        return None
    for entry in lib_dir.iterdir():
        match = re.fullmatch(r"python(3\.\d+)", entry.name)
        if match and entry.is_dir():
            return match.group(1)
    return None
