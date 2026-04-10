# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from . import PYPROJECT_JSON_PATTERN
from .pyproject_parse_result import PyProjectParseResult
from .pyproject_json import parse_pyproject_json


def _write_base_toml_content(data: dict) -> str:
    """
    Write minimal TOML content with project and tool.pyside6-project sections.
    """
    lines = []

    if data.get('project'):
        lines.append('[project]')
        for key, value in sorted(data['project'].items()):
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')

    if data.get("tool") and data['tool'].get('pyside6-project'):
        lines.append('\n[tool.pyside6-project]')
        for key, value in sorted(data['tool']['pyside6-project'].items()):
            if isinstance(value, list):
                items = [f'"{item}"' for item in sorted(value)]
                lines.append(f'{key} = [{", ".join(items)}]')
            else:
                lines.append(f'{key} = "{value}"')

    return '\n'.join(lines)


def parse_pyproject_toml(pyproject_toml_file: Path) -> PyProjectParseResult:
    """
    Parse a pyproject.toml file and return a PyProjectParseResult object.
    """
    result = PyProjectParseResult()

    try:
        content = pyproject_toml_file.read_text(encoding='utf-8')
        root_table = tomllib.loads(content)
    except Exception as e:
        result.errors.append(str(e))
        return result

    tool_entry = root_table.get("tool", {})
    pyside_table = tool_entry.get("pyside6-project", {})
    if not pyside_table:
        result.errors.append("Missing [tool.pyside6-project] table")
        return result

    if rcc_table := tool_entry.get("pyside6-rcc", {}):
        result.rcc_options = rcc_table.get("options", [])

    if uic_table := tool_entry.get("pyside6-uic", {}):
        result.uic_options = uic_table.get("options", [])

    files = pyside_table.get("files", [])
    if not isinstance(files, list):
        result.errors.append("Missing or invalid files list")
        return result

    # Convert paths
    for file in files:
        if not isinstance(file, str):
            result.errors.append(f"Invalid file: {file}")
            return result
        file_path = Path(file)
        if not file_path.is_absolute():
            file_path = (pyproject_toml_file.parent / file).resolve()
        result.files.append(file_path)

    return result


def write_pyproject_toml(pyproject_file: Path, project_name: str, project_files: list[str]):
    """
    Create or overwrite a pyproject.toml file with the specified content.
    """
    data = {
        "project": {"name": project_name},
        "tool": {
            "pyside6-project": {"files": sorted(project_files)}
        }
    }

    content = _write_base_toml_content(data)
    try:
        pyproject_file.write_text(content, encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Error writing TOML file: {str(e)}")


def robust_relative_to_posix(target_path: Path, base_path: Path) -> str:
    """
    Calculates the relative path from base_path to target_path.
    Uses Path.relative_to first, falls back to os.path.relpath if it fails.
    Returns the result as a POSIX path string.
    """
    # Ensure both paths are absolute for reliable calculation, although in this specific code,
    # project_folder and paths in output_files are expected to be resolved/absolute already.
    abs_target = target_path.resolve() if not target_path.is_absolute() else target_path
    abs_base = base_path.resolve() if not base_path.is_absolute() else base_path

    try:
        return abs_target.relative_to(abs_base).as_posix()
    except ValueError:
        # Fallback to os.path.relpath which is more robust for paths that are not direct subpaths.
        relative_str = os.path.relpath(str(abs_target), str(abs_base))
        # Convert back to Path temporarily to get POSIX format
        return Path(relative_str).as_posix()


def migrate_pyproject(pyproject_file: Path | str = None) -> int:
    """
    Migrate a project *.pyproject JSON file to the new pyproject.toml format.

    The containing subprojects are migrated recursively.

    :return: 0 if successful, 1 if an error occurred.
    """
    project_name = None

    # Transform the user input string into a Path object
    if isinstance(pyproject_file, str):
        pyproject_file = Path(pyproject_file)

    if pyproject_file:
        if not pyproject_file.match(PYPROJECT_JSON_PATTERN):
            print(f"Cannot migrate non \"{PYPROJECT_JSON_PATTERN}\" file:", file=sys.stderr)
            print(f"\"{pyproject_file}\"", file=sys.stderr)
            return 1
        project_files = [pyproject_file]
        project_name = pyproject_file.stem
    else:
        # Get the existing *.pyproject files in the current directory
        project_files = list(Path().glob(PYPROJECT_JSON_PATTERN))
        if not project_files:
            print(f"No project file found in the current directory: {Path()}", file=sys.stderr)
            return 1
        if len(project_files) > 1:
            print("Multiple pyproject files found in the project folder:")
            print('\n'.join(str(project_file) for project_file in project_files))
            response = input("Continue? y/n: ")
            if response.lower().strip() not in {"yes", "y"}:
                return 0
        else:
            # If there is only one *.pyproject file in the current directory,
            # use its file name as the project name
            project_name = project_files[0].stem

    # The project files that will be written to the pyproject.toml file
    output_files: set[Path] = set()
    for project_file in project_files:
        project_data = parse_pyproject_json(project_file)
        if project_data.errors:
            print(f"Invalid project file: {project_file}. Errors found:", file=sys.stderr)
            print('\n'.join(project_data.errors), file=sys.stderr)
            return 1
        output_files.update(project_data.files)

    project_folder = project_files[0].parent.resolve()
    if project_name is None:
        # If a project name has not resolved, use the name of the parent folder
        project_name = project_folder.name

    pyproject_toml_file = project_folder / "pyproject.toml"

    relative_files = sorted(
        robust_relative_to_posix(p, project_folder) for p in output_files
    )

    if not (already_existing_file := pyproject_toml_file.exists()):
        # Create new pyproject.toml file
        data = {
            "project": {"name": project_name},
            "tool": {
                "pyside6-project": {"files": relative_files}
            }
        }
        updated_content = _write_base_toml_content(data)
    else:
        # For an already existing file, append our tool.pyside6-project section
        # If the project section is missing, add it
        try:
            content = pyproject_toml_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error processing existing TOML file: {str(e)}", file=sys.stderr)
            return 1

        append_content = []

        if '[project]' not in content:
            # Add project section if needed
            append_content.append('\n[project]')
            append_content.append(f'name = "{project_name}"')

        if '[tool.pyside6-project]' not in content:
            # Add tool.pyside6-project section
            append_content.append('\n[tool.pyside6-project]')
            items = [f'"{item}"' for item in relative_files]
            append_content.append(f'files = [{", ".join(items)}]')

        if append_content:
            updated_content = content.rstrip() + '\n' + '\n'.join(append_content)
        else:
            # No changes needed
            print("pyproject.toml already contains [project] and [tool.pyside6-project] sections")
            return 0

        print(f"WARNING: A pyproject.toml file already exists at \"{pyproject_toml_file}\"")
        print("The file will be updated with the following content:")
        print(updated_content)
        response = input("Proceed? [Y/n] ")
        if response.lower().strip() not in {"yes", "y"}:
            return 0

    try:
        pyproject_toml_file.write_text(updated_content, encoding='utf-8')
    except Exception as e:
        print(f"Error writing to \"{pyproject_toml_file}\": {str(e)}", file=sys.stderr)
        return 1

    if not already_existing_file:
        print(f"Created \"{pyproject_toml_file}\"")
    else:
        print(f"Updated \"{pyproject_toml_file}\"")

    # Recursively migrate the subprojects
    for sub_project_file in filter(lambda f: f.match(PYPROJECT_JSON_PATTERN), output_files):
        result = migrate_pyproject(sub_project_file)
        if result != 0:
            return result
    return 0
