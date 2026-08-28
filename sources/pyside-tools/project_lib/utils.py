# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool
from __future__ import annotations

import sys
from pathlib import Path

from . import (QTPATHS_CMD, PYPROJECT_JSON_PATTERN, PYPROJECT_TOML_PATTERN, PYPROJECT_FILE_PATTERNS,
               ClOptions)
from .commands import qtpaths
from .pyproject_toml import parse_pyproject_toml
from .pyproject_json import parse_pyproject_json
from .qrc import qrc_file_requires_rebuild

_qt_metatype_json_dir: Path | None = None


def requires_rebuild(sources: list[Path], artifact: Path) -> bool:
    """Returns whether artifact needs to be rebuilt depending on sources"""
    if not artifact.is_file():
        return True

    artifact_mod_time = artifact.stat().st_mtime
    for source in sources:
        if source.stat().st_mtime > artifact_mod_time:
            return True
        # The .qrc file references other files that might have changed
        if source.suffix == ".qrc" and qrc_file_requires_rebuild(source, artifact):
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


def resolve_valid_project_file(
    project_path_input: str = None, project_file_patterns: list[str] = PYPROJECT_FILE_PATTERNS
) -> Path:
    """
    Find a valid project file given a preferred project file name and a list of project file name
    patterns for a fallback search.

    If the provided file name is a valid project file, return it. Otherwise, search for a known
    project file in the current working directory with the given patterns.

    Raises a ValueError if no project file is found, multiple project files are found in the same
    directory or the provided path is not a valid project file or folder.

    :param project_path_input: The command-line argument specifying a project file or folder path.
    :param project_file_patterns: The list of project file patterns to search for.

    :return: The resolved project file path
    """
    if project_path_input and (project_file := Path(project_path_input).resolve()).is_file():
        if project_file.match(PYPROJECT_TOML_PATTERN):
            if bool(parse_pyproject_toml(project_file).errors):
                raise ValueError(f"Invalid project file: {project_file}")
        elif project_file.match(PYPROJECT_JSON_PATTERN):
            pyproject_json_result = parse_pyproject_json(project_file)
            if errors := '\n'.join(str(e) for e in pyproject_json_result.errors):
                raise ValueError(f"Invalid project file: {project_file}\n{errors}")
        else:
            raise ValueError(f"Unknown project file: {project_file}")
        return project_file

    project_folder = Path.cwd()
    if project_path_input:
        if not Path(project_path_input).resolve().is_dir():
            raise ValueError(f"Invalid project path: {project_path_input}")
        project_folder = Path(project_path_input).resolve()

    # Search a project file in the project folder using the provided patterns
    for pattern in project_file_patterns:
        if not (matches := list(project_folder.glob(pattern))):
            # No project files found with the specified pattern
            continue

        if len(matches) > 1:
            matched_files = '\n'.join(str(f) for f in matches)
            raise ValueError(f"Multiple project files found:\n{matched_files}")

        project_file = matches[0]

        if pattern == PYPROJECT_TOML_PATTERN:
            if parse_pyproject_toml(project_file).errors:
                # Invalid file, but a .pyproject file may exist
                # We can not raise an error due to ensuring backward compatibility
                continue
        elif pattern == PYPROJECT_JSON_PATTERN:
            pyproject_json_result = parse_pyproject_json(project_file)
            if errors := '\n'.join(str(e) for e in pyproject_json_result.errors):
                raise ValueError(f"Invalid project file: {project_file}\n{errors}")

        # Found a valid project file
        return project_file

    raise ValueError("No project file found in the current directory")
