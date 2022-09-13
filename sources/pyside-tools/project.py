# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


"""
Builds a '.pyproject' file

Builds Qt Designer forms, resource files and QML type files.

Deploys the application by creating an executable for the corresponding platform

For each entry in a '.pyproject' file:
- <name>.pyproject: Recurse to handle subproject
- <name>.qrc      : Runs the resource compiler to create a file rc_<name>.py
- <name>.ui       : Runs the user interface compiler to create a file ui_<name>.py

For a Python file declaring a QML module, a directory matching the URI is
created and populated with .qmltypes and qmldir files for use by code analysis
tools. Currently, only one QML module consisting of several classes can be
handled per project file.
"""

import json
import os
import subprocess
import sys

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


MODE_HELP = """build    Builds the project
run      Builds the project and runs the first file")
clean    Cleans the build artifacts")
qmllint  Runs the qmllint tool
deploy   Deploys the application"""


opt_quiet = False
opt_dry_run = False
opt_force = False
opt_qml_module = False


UIC_CMD = "pyside6-uic"
RCC_CMD = "pyside6-rcc"
MOD_CMD = "pyside6-metaobjectdump"
QMLTYPEREGISTRAR_CMD = "pyside6-qmltyperegistrar"
QMLLINT_CMD = "pyside6-qmllint"
DEPLOY_CMD = "pyside6-deploy"
QTPATHS_CMD = "qtpaths6"


PROJECT_FILE_SUFFIX = ".pyproject"
QMLDIR_FILE = "qmldir"


QML_IMPORT_NAME = "QML_IMPORT_NAME"
QML_IMPORT_MAJOR_VERSION = "QML_IMPORT_MAJOR_VERSION"
QML_IMPORT_MINOR_VERSION = "QML_IMPORT_MINOR_VERSION"
QT_MODULES = "QT_MODULES"


METATYPES_JSON_SUFFIX = "_metatypes.json"


def run_command(command: List[str], cwd: str = None, ignore_fail: bool = False):
    """Run a command observing quiet/dry run"""
    if not opt_quiet or opt_dry_run:
        print(" ".join(command))
    if not opt_dry_run:
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
    if not path.exists():
        return
    if not opt_quiet:
        print(f"Removing {path.name}...")
    if opt_dry_run:
        return
    _remove_path_recursion(path)


def package_dir() -> Path:
    """Return the PySide6 root."""
    return Path(__file__).resolve().parents[1]


_qtpaths_info: Dict[str, str] = {}


def qtpaths() -> Dict[str, str]:
    """Run qtpaths and return a dict of values."""
    global _qtpaths_info
    if not _qtpaths_info:
        output = subprocess.check_output([QTPATHS_CMD, "--query"])
        for line in output.decode("utf-8").split("\n"):
            tokens = line.strip().split(":")
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
        metatypes_dir = qt_dir / "lib" / "metatypes"
        if metatypes_dir.is_dir():  # Fully installed case
            _qt_metatype_json_dir = metatypes_dir
        else:
            # Fallback for distro builds/development.
            print(f"Falling back to {QTPATHS_CMD} to determine metatypes directory.",
                  file=sys.stderr)
            _qt_metatype_json_dir = Path(qtpaths()["QT_INSTALL_LIBS"]) / "metatypes"
    return _qt_metatype_json_dir


class QmlProjectData:
    """QML relevant project data."""

    def __init__(self):
        self._import_name: str = ""
        self._import_major_version: int = 0
        self._import_minor_version: int = 0
        self._qt_modules: List[str] = []

    def registrar_options(self):
        result = ["--import-name", self._import_name,
                  "--major-version", str(self._import_major_version),
                  "--minor-version", str(self._import_minor_version)]
        if self._qt_modules:
            # Add Qt modules as foreign types
            foreign_files: List[str] = []
            meta_dir = qt_metatype_json_dir()
            for mod in self._qt_modules:
                mod_id = mod[2:].lower()
                pattern = f"qt6{mod_id}_*{METATYPES_JSON_SUFFIX}"
                for f in meta_dir.glob(pattern):
                    foreign_files.append(os.fspath(f))
                    break
                list = ",".join(foreign_files)
                result.append(f"--foreign-types={list}")
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


def _check_qml_decorators(py_file: Path) -> Tuple[bool, QmlProjectData]:
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


class Project:
    def __init__(self, project_file: Path):
        """Parse the project."""
        self._project_file = project_file

        # All sources except subprojects
        self._files: List[Path] = []
        # QML files
        self._qml_files: List[Path] = []
        self._sub_projects: List[Project] = []
        # Python files
        self._main_file: Path = None
        self._python_files: List[Path] = []

        # Files for QML modules using the QmlElement decorators
        self._qml_module_sources: List[Path] = []
        self._qml_module_dir: Optional[Path] = None
        self._qml_dir_file: Optional[Path] = None
        self._qml_project_data = QmlProjectData()

        with project_file.open("r") as pyf:
            pyproject = json.load(pyf)
            for f in pyproject["files"]:
                file = Path(project_file.parent / f)
                if file.suffix == PROJECT_FILE_SUFFIX:
                    self._sub_projects.append(Project(file))
                else:
                    self._files.append(file)
                    if file.suffix == ".qml":
                        self._qml_files.append(file)
                    elif file.suffix == ".py":
                        if file.name == "main.py":
                            self._main_file = file
                        self._python_files.append(file)
        if not self._main_file:
            self._find_main_file()
        self._qml_module_check()

    @property
    def project_file(self):
        return self._project_file

    @property
    def files(self):
        return self._files

    @property
    def main_file(self):
        return self._main_file

    @property
    def python_files(self):
        return self._python_files

    def _find_main_file(self) -> str:
        """ Find the entry point file containing the main function"""

        def is_main(file):
            return "__main__" in file.read_text(encoding="utf-8")

        if not self.main_file:
            for python_file in self.python_files:
                if is_main(python_file):
                    self.main_file = python_file
                    return str(python_file)

        # __main__ not found
        print("Python file with main function not found. Add the file to"
              f" {project_file}", file=sys.stderr)
        sys.exit(1)

    def _qml_module_check(self):
        """Run a pre-check on Python source files and find the ones with QML
           decorators (representing a QML module)."""
        # Quick check for any QML files (to avoid running moc for no reason).
        if not opt_qml_module and not self._qml_files:
            return
        for file in self.files:
            if file.suffix == ".py":
                has_class, data = _check_qml_decorators(file)
                if has_class:
                    self._qml_module_sources.append(file)
                    if data:
                        self._qml_project_data = data

        if not self._qml_module_sources:
            return
        if not self._qml_project_data:
            print("Detected QML-decorated files, "
                  "but was unable to detect QML_IMPORT_NAME")
            sys.exit(1)

        self._qml_module_dir = self._project_file.parent
        for uri_dir in self._qml_project_data.import_name.split("."):
            self._qml_module_dir /= uri_dir
        print(self._qml_module_dir)
        self._qml_dir_file = self._qml_module_dir / QMLDIR_FILE

        if not opt_quiet:
            count = len(self._qml_module_sources)
            print(f"{self._project_file.name}, {count} QML file(s), {self._qml_project_data}")

    def _get_artifact(self, file: Path) -> Tuple[Optional[Path], Optional[List[str]]]:
        """Return path and command for a file's artifact"""
        if file.suffix == ".ui":  # Qt form files
            py_file = f"{file.parent}/ui_{file.stem}.py"
            return (Path(py_file), [UIC_CMD, os.fspath(file), "-o", py_file])
        if file.suffix == ".qrc":  # Qt resources
            py_file = f"{file.parent}/rc_{file.stem}.py"
            return (Path(py_file), [RCC_CMD, os.fspath(file), "-o", py_file])
        # generate .qmltypes from sources with Qml decorators
        if file.suffix == ".py" and file in self._qml_module_sources:
            assert self._qml_module_dir
            qml_module_dir = os.fspath(self._qml_module_dir)
            json_file = f"{qml_module_dir}/{file.stem}{METATYPES_JSON_SUFFIX}"
            return (Path(json_file), [MOD_CMD, "-o", json_file, os.fspath(file)])
        # Run qmltyperegistrar
        if file.name.endswith(METATYPES_JSON_SUFFIX):
            assert self._qml_module_dir
            stem = file.name[: len(file.name) - len(METATYPES_JSON_SUFFIX)]
            qmltypes_file = self._qml_module_dir / f"{stem}.qmltypes"
            cmd = [QMLTYPEREGISTRAR_CMD, "--generate-qmltypes",
                os.fspath(qmltypes_file),"-o", os.devnull, os.fspath(file)]
            cmd.extend(self._qml_project_data.registrar_options())
            return (qmltypes_file, cmd)

        return (None, None)

    def _regenerate_qmldir(self):
        """Regenerate the 'qmldir' file."""
        if opt_dry_run or not self._qml_dir_file:
            return
        if opt_force or requires_rebuild(self._qml_module_sources, self._qml_dir_file):
            with self._qml_dir_file.open("w") as qf:
                qf.write(f"module {self._qml_project_data.import_name}\n")
                for f in self._qml_module_dir.glob("*.qmltypes"):
                    qf.write(f"typeinfo {f.name}\n")

    def _build_file(self, source: Path):
        """Build an artifact."""
        artifact, command = self._get_artifact(source)
        if not artifact:
            return
        if opt_force or requires_rebuild([source], artifact):
            run_command(command, cwd=self._project_file.parent)
        self._build_file(artifact)  # Recurse for QML (json->qmltypes)

    def build(self):
        """Build."""
        for sub_project in self._sub_projects:
            sub_project.build()
        if self._qml_module_dir:
            self._qml_module_dir.mkdir(exist_ok=True, parents=True)
        for file in self._files:
            self._build_file(file)
        self._regenerate_qmldir()

    def run(self):
        """Runs the project"""
        self.build()
        cmd = [sys.executable, str(self.main_file)]
        run_command(cmd, cwd=self._project_file.parent)

    def _clean_file(self, source: Path):
        """Clean an artifact."""
        artifact, command = self._get_artifact(source)
        if artifact and artifact.is_file():
            remove_path(artifact)
            self._clean_file(artifact)  # Recurse for QML (json->qmltypes)

    def clean(self):
        """Clean build artifacts."""
        for sub_project in self._sub_projects:
            sub_project.clean()
        for file in self._files:
            self._clean_file(file)
        if self._qml_module_dir and self._qml_module_dir.is_dir():
            remove_path(self._qml_module_dir)
            # In case of a dir hierarchy ("a.b" -> a/b), determine and delete
            # the root directory
            if self._qml_module_dir.parent != self._project_file.parent:
                project_dir_parts = len(self._project_file.parent.parts)
                first_module_dir = self._qml_module_dir.parts[project_dir_parts]
                remove_path(self._project_file.parent / first_module_dir)

    def _qmllint(self):
        """Helper for running qmllint on .qml files (non-recursive)."""
        if not self._qml_files:
            print(f"{self._project_file.name}: No QML files found", file=sys.stderr)
            return

        cmd = [QMLLINT_CMD]
        if self._qml_dir_file:
            cmd.extend(["-i", os.fspath(self._qml_dir_file)])
        for f in self._qml_files:
            cmd.append(os.fspath(f))
        run_command(cmd, cwd=self._project_file.parent, ignore_fail=True)

    def qmllint(self):
        """Run qmllint on .qml files."""
        self.build()
        for sub_project in self._sub_projects:
            sub_project._qmllint()
        self._qmllint()

    def deploy(self):
        """Deploys the application"""
        cmd = [DEPLOY_CMD]
        cmd.extend([str(self.main_file), "-f"])
        run_command(cmd, cwd=self._project_file.parent)


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


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Only print commands")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild")
    parser.add_argument("--qml-module", "-Q", action="store_true",
                        help="Perform check for QML module")
    parser.add_argument("mode",
                        choices=["build", "run", "clean", "qmllint", "deploy"],
                        default="build", type=str, help=MODE_HELP)
    parser.add_argument("file", help="Project file", nargs="?", type=str)

    options = parser.parse_args()
    opt_quiet = options.quiet
    opt_dry_run = options.dry_run
    opt_force = options.force
    opt_qml_module = options.qml_module
    mode = options.mode
    project_file = resolve_project_file(options.file)
    if not project_file:
        print(f"Cannot determine project_file {options.file}", file=sys.stderr)
        sys.exit(1)
    project = Project(project_file)
    if mode == "build":
        project.build()
    elif mode == "run":
        project.run()
    elif mode == "clean":
        project.clean()
    elif mode == "qmllint":
        project.qmllint()
    elif mode == "deploy":
        project.deploy()
    else:
        print(f"Invalid mode {mode}", file=sys.stderr)
        sys.exit(1)
