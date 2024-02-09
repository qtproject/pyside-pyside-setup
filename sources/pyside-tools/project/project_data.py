# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import json
import os
import subprocess
import sys
from typing import List, Tuple
from pathlib import Path
from . import (METATYPES_JSON_SUFFIX, PROJECT_FILE_SUFFIX, TRANSLATION_SUFFIX,
               qt_metatype_json_dir, MOD_CMD, QML_IMPORT_MAJOR_VERSION,
               QML_IMPORT_MINOR_VERSION, QML_IMPORT_NAME, QT_MODULES)


def is_python_file(file: Path) -> bool:
    return (file.suffix == ".py"
            or sys.platform == "win32" and file.suffix == ".pyw")


class ProjectData:
    def __init__(self, project_file: Path) -> None:
        """Parse the project."""
        self._project_file = project_file
        self._sub_projects_files: List[Path] = []

        # All sources except subprojects
        self._files: List[Path] = []
        # QML files
        self._qml_files: List[Path] = []
        # Python files
        self.main_file: Path = None
        self._python_files: List[Path] = []
        # ui files
        self._ui_files: List[Path] = []
        # qrc files
        self._qrc_files: List[Path] = []
        # ts files
        self._ts_files: List[Path] = []

        with project_file.open("r") as pyf:
            pyproject = json.load(pyf)
            for f in pyproject["files"]:
                file = Path(project_file.parent / f)
                if file.suffix == PROJECT_FILE_SUFFIX:
                    self._sub_projects_files.append(file)
                else:
                    self._files.append(file)
                    if file.suffix == ".qml":
                        self._qml_files.append(file)
                    elif is_python_file(file):
                        if file.stem == "main":
                            self.main_file = file
                        self._python_files.append(file)
                    elif file.suffix == ".ui":
                        self._ui_files.append(file)
                    elif file.suffix == ".qrc":
                        self._qrc_files.append(file)
                    elif file.suffix == TRANSLATION_SUFFIX:
                        self._ts_files.append(file)

        if not self.main_file:
            self._find_main_file()

    @property
    def project_file(self):
        return self._project_file

    @property
    def files(self):
        return self._files

    @property
    def main_file(self):
        return self._main_file

    @main_file.setter
    def main_file(self, main_file):
        self._main_file = main_file

    @property
    def python_files(self):
        return self._python_files

    @property
    def ui_files(self):
        return self._ui_files

    @property
    def qrc_files(self):
        return self._qrc_files

    @property
    def qml_files(self):
        return self._qml_files

    @property
    def ts_files(self):
        return self._ts_files

    @property
    def sub_projects_files(self):
        return self._sub_projects_files

    def _find_main_file(self) -> str:
        """Find the entry point file containing the main function"""

        def is_main(file):
            return "__main__" in file.read_text(encoding="utf-8")

        if not self.main_file:
            for python_file in self.python_files:
                if is_main(python_file):
                    self.main_file = python_file
                    return str(python_file)

        # __main__ not found
        print(
            "Python file with main function not found. Add the file to" f" {self.project_file}",
            file=sys.stderr,
        )
        sys.exit(1)


class QmlProjectData:
    """QML relevant project data."""

    def __init__(self):
        self._import_name: str = ""
        self._import_major_version: int = 0
        self._import_minor_version: int = 0
        self._qt_modules: List[str] = []

    def registrar_options(self):
        result = [
            "--import-name",
            self._import_name,
            "--major-version",
            str(self._import_major_version),
            "--minor-version",
            str(self._import_minor_version),
        ]
        if self._qt_modules:
            # Add Qt modules as foreign types
            foreign_files: List[str] = []
            meta_dir = qt_metatype_json_dir()
            for mod in self._qt_modules:
                mod_id = mod[2:].lower()
                pattern = f"qt6{mod_id}_*"
                if sys.platform != "win32":
                    pattern += "_"  # qt6core_debug_metatypes.json (Linux)
                pattern += METATYPES_JSON_SUFFIX
                for f in meta_dir.glob(pattern):
                    foreign_files.append(os.fspath(f))
                    break
                if foreign_files:
                    foreign_files_str = ",".join(foreign_files)
                    result.append(f"--foreign-types={foreign_files_str}")
        return result

    @property
    def import_name(self):
        return self._import_name

    @import_name.setter
    def import_name(self, n):
        self._import_name = n

    @property
    def import_major_version(self):
        return self._import_major_version

    @import_major_version.setter
    def import_major_version(self, v):
        self._import_major_version = v

    @property
    def import_minor_version(self):
        return self._import_minor_version

    @import_minor_version.setter
    def import_minor_version(self, v):
        self._import_minor_version = v

    @property
    def qt_modules(self):
        return self._qt_modules

    @qt_modules.setter
    def qt_modules(self, v):
        self._qt_modules = v

    def __str__(self) -> str:
        vmaj = self._import_major_version
        vmin = self._import_minor_version
        return f'"{self._import_name}" v{vmaj}.{vmin}'

    def __bool__(self) -> bool:
        return len(self._import_name) > 0 and self._import_major_version > 0


def _has_qml_decorated_class(class_list: List) -> bool:
    """Check for QML-decorated classes in the moc json output."""
    for d in class_list:
        class_infos = d.get("classInfos")
        if class_infos:
            for e in class_infos:
                if "QML" in e["name"]:
                    return True
    return False


def check_qml_decorators(py_file: Path) -> Tuple[bool, QmlProjectData]:
    """Check if a Python file has QML-decorated classes by running a moc check
    and return whether a class was found and the QML data."""
    data = None
    try:
        cmd = [MOD_CMD, "--quiet", os.fspath(py_file)]
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            data = json.load(proc.stdout)
            proc.wait()
    except Exception as e:
        t = type(e).__name__
        print(f"{t}: running {MOD_CMD} on {py_file}: {e}", file=sys.stderr)
        sys.exit(1)

    qml_project_data = QmlProjectData()
    if not data:
        return (False, qml_project_data)  # No classes in file

    first = data[0]
    class_list = first["classes"]
    has_class = _has_qml_decorated_class(class_list)
    if has_class:
        v = first.get(QML_IMPORT_NAME)
        if v:
            qml_project_data.import_name = v
        v = first.get(QML_IMPORT_MAJOR_VERSION)
        if v:
            qml_project_data.import_major_version = v
            qml_project_data.import_minor_version = first.get(QML_IMPORT_MINOR_VERSION)
        v = first.get(QT_MODULES)
        if v:
            qml_project_data.qt_modules = v
    return (has_class, qml_project_data)
