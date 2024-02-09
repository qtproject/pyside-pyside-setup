# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

from . import QTPATHS_CMD, PROJECT_FILE_SUFFIX, ClOptions


def run_command(command: List[str], cwd: str = None, ignore_fail: bool = False):
    """Run a command observing quiet/dry run"""
    cloptions = ClOptions()
    if not cloptions.quiet or cloptions.dry_run:
        print(" ".join(command))
    if not cloptions.dry_run:
        ex = subprocess.call(command, cwd=cwd)
        if ex != 0 and not ignore_fail:
            sys.exit(ex)


def requires_rebuild(sources: List[Path], artifact: Path) -> bool:
    """Returns whether artifact needs to be rebuilt depending on sources"""
    if not artifact.is_file():
        return True
    artifact_mod_time = artifact.stat().st_mtime
    for source in sources:
        if source.stat().st_mtime > artifact_mod_time:
            return True
    return False


def _remove_path_recursion(path: Path):
    """Recursion to remove a file or directory."""
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        for item in path.iterdir():
            _remove_path_recursion(item)
        path.rmdir()


def remove_path(path: Path):
    """Remove path (file or directory) observing opt_dry_run."""
    cloptions = ClOptions()
    if not path.exists():
        return
    if not cloptions.quiet:
        print(f"Removing {path.name}...")
    if cloptions.dry_run:
        return
    _remove_path_recursion(path)


def package_dir() -> Path:
    """Return the PySide6 root."""
    return Path(__file__).resolve().parents[2]


_qtpaths_info: Dict[str, str] = {}


def qtpaths() -> Dict[str, str]:
    """Run qtpaths and return a dict of values."""
    global _qtpaths_info
    if not _qtpaths_info:
        output = subprocess.check_output([QTPATHS_CMD, "--query"])
        for line in output.decode("utf-8").split("\n"):
            tokens = line.strip().split(":", maxsplit=1)  # "Path=C:\..."
            if len(tokens) == 2:
                _qtpaths_info[tokens[0]] = tokens[1]
    return _qtpaths_info


_qt_metatype_json_dir: Optional[Path] = None


def qt_metatype_json_dir() -> Path:
    """Return the location of the Qt QML metatype files."""
    global _qt_metatype_json_dir
    if not _qt_metatype_json_dir:
        qt_dir = package_dir()
        if sys.platform != "win32":
            qt_dir /= "Qt"
        metatypes_dir = qt_dir / "metatypes"
        if metatypes_dir.is_dir():  # Fully installed case
            _qt_metatype_json_dir = metatypes_dir
        else:
            # Fallback for distro builds/development.
            print(
                f"Falling back to {QTPATHS_CMD} to determine metatypes directory.", file=sys.stderr
            )
            _qt_metatype_json_dir = Path(qtpaths()["QT_INSTALL_ARCHDATA"]) / "metatypes"
    return _qt_metatype_json_dir


def resolve_project_file(cmdline: str) -> Optional[Path]:
    """Return the project file from the command  line value, either
    from the file argument or directory"""
    project_file = Path(cmdline).resolve() if cmdline else Path.cwd()
    if project_file.is_file():
        return project_file
    if project_file.is_dir():
        for m in project_file.glob(f"*{PROJECT_FILE_SUFFIX}"):
            return m
    return None
