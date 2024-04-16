# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


"""
Builds a '.pyproject' file

Builds Qt Designer forms, resource files and QML type files

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
import sys
import os
from typing import List, Tuple, Optional
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter

from project import (QmlProjectData, check_qml_decorators, is_python_file,
                     QMLDIR_FILE, MOD_CMD, METATYPES_JSON_SUFFIX,
                     SHADER_SUFFIXES, TRANSLATION_SUFFIX,
                     requires_rebuild, run_command, remove_path,
                     ProjectData, resolve_project_file, new_project,
                     ProjectType, ClOptions)

MODE_HELP = """build    Builds the project
run        Builds the project and runs the first file")
clean      Cleans the build artifacts")
qmllint    Runs the qmllint tool
deploy     Deploys the application
lupdate    Updates translation (.ts) files
new-ui     Creates a new QtWidgets project with a Qt Designer-based main window
new-widget Creates a new QtWidgets project with a main window
new-quick  Creates a new QtQuick project
"""

UIC_CMD = "pyside6-uic"
RCC_CMD = "pyside6-rcc"
LRELEASE_CMD = "pyside6-lrelease"
LUPDATE_CMD = "pyside6-lupdate"
QMLTYPEREGISTRAR_CMD = "pyside6-qmltyperegistrar"
QMLLINT_CMD = "pyside6-qmllint"
QSB_CMD = "pyside6-qsb"
DEPLOY_CMD = "pyside6-deploy"

NEW_PROJECT_TYPES = {"new-quick": ProjectType.QUICK,
                     "new-ui": ProjectType.WIDGET_FORM,
                     "new-widget": ProjectType.WIDGET}


def _sort_sources(files: List[Path]) -> List[Path]:
    """Sort the sources for building, ensure .qrc is last since it might depend
       on generated files."""

    def key_func(p: Path):
        return p.suffix if p.suffix != ".qrc" else ".zzzz"

    return sorted(files, key=key_func)


class Project:
    """
    Class to wrap the various operations on Project
    """
    def __init__(self, project_file: Path):
        self.project = ProjectData(project_file=project_file)
        self.cl_options = ClOptions()

        # Files for QML modules using the QmlElement decorators
        self._qml_module_sources: List[Path] = []
        self._qml_module_dir: Optional[Path] = None
        self._qml_dir_file: Optional[Path] = None
        self._qml_project_data = QmlProjectData()
        self._qml_module_check()

    def _qml_module_check(self):
        """Run a pre-check on Python source files and find the ones with QML
        decorators (representing a QML module)."""
        # Quick check for any QML files (to avoid running moc for no reason).
        if not self.cl_options.qml_module and not self.project.qml_files:
            return
        for file in self.project.files:
            if is_python_file(file):
                has_class, data = check_qml_decorators(file)
                if has_class:
                    self._qml_module_sources.append(file)
                    if data:
                        self._qml_project_data = data

        if not self._qml_module_sources:
            return
        if not self._qml_project_data:
            print("Detected QML-decorated files, " "but was unable to detect QML_IMPORT_NAME")
            sys.exit(1)

        self._qml_module_dir = self.project.project_file.parent
        for uri_dir in self._qml_project_data.import_name.split("."):
            self._qml_module_dir /= uri_dir
        print(self._qml_module_dir)
        self._qml_dir_file = self._qml_module_dir / QMLDIR_FILE

        if not self.cl_options.quiet:
            count = len(self._qml_module_sources)
            print(f"{self.project.project_file.name}, {count} QML file(s),"
                  f" {self._qml_project_data}")

    def _get_artifacts(self, file: Path) -> Tuple[List[Path], Optional[List[str]]]:
        """Return path and command for a file's artifact"""
        if file.suffix == ".ui":  # Qt form files
            py_file = f"{file.parent}/ui_{file.stem}.py"
            return ([Path(py_file)], [UIC_CMD, os.fspath(file), "--rc-prefix", "-o", py_file])
        if file.suffix == ".qrc":  # Qt resources
            py_file = f"{file.parent}/rc_{file.stem}.py"
            return ([Path(py_file)], [RCC_CMD, os.fspath(file), "-o", py_file])
        # generate .qmltypes from sources with Qml decorators
        if file.suffix == ".py" and file in self._qml_module_sources:
            assert self._qml_module_dir
            qml_module_dir = os.fspath(self._qml_module_dir)
            json_file = f"{qml_module_dir}/{file.stem}{METATYPES_JSON_SUFFIX}"
            return ([Path(json_file)], [MOD_CMD, "-o", json_file, os.fspath(file)])
        # Run qmltyperegistrar
        if file.name.endswith(METATYPES_JSON_SUFFIX):
            assert self._qml_module_dir
            stem = file.name[: len(file.name) - len(METATYPES_JSON_SUFFIX)]
            qmltypes_file = self._qml_module_dir / f"{stem}.qmltypes"
            cpp_file = self._qml_module_dir / f"{stem}_qmltyperegistrations.cpp"
            cmd = [QMLTYPEREGISTRAR_CMD, "--generate-qmltypes",
                   os.fspath(qmltypes_file), "-o", os.fspath(cpp_file),
                   os.fspath(file)]
            cmd.extend(self._qml_project_data.registrar_options())
            return ([qmltypes_file, cpp_file], cmd)

        if file.name.endswith(TRANSLATION_SUFFIX):
            qm_file = f"{file.parent}/{file.stem}.qm"
            cmd = [LRELEASE_CMD, os.fspath(file), "-qm", qm_file]
            return ([Path(qm_file)], cmd)

        if file.suffix in SHADER_SUFFIXES:
            qsb_file = f"{file.parent}/{file.stem}.qsb"
            cmd = [QSB_CMD, "-o", qsb_file, os.fspath(file)]
            return ([Path(qsb_file)], cmd)

        return ([], None)

    def _regenerate_qmldir(self):
        """Regenerate the 'qmldir' file."""
        if self.cl_options.dry_run or not self._qml_dir_file:
            return
        if self.cl_options.force or requires_rebuild(self._qml_module_sources, self._qml_dir_file):
            with self._qml_dir_file.open("w") as qf:
                qf.write(f"module {self._qml_project_data.import_name}\n")
                for f in self._qml_module_dir.glob("*.qmltypes"):
                    qf.write(f"typeinfo {f.name}\n")

    def _build_file(self, source: Path):
        """Build an artifact."""
        artifacts, command = self._get_artifacts(source)
        for artifact in artifacts:
            if self.cl_options.force or requires_rebuild([source], artifact):
                run_command(command, cwd=self.project.project_file.parent)
            self._build_file(artifact)  # Recurse for QML (json->qmltypes)

    def build(self):
        """Build."""
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file).build()
        if self._qml_module_dir:
            self._qml_module_dir.mkdir(exist_ok=True, parents=True)
        for file in _sort_sources(self.project.files):
            self._build_file(file)
        self._regenerate_qmldir()

    def run(self):
        """Runs the project"""
        self.build()
        cmd = [sys.executable, str(self.project.main_file)]
        run_command(cmd, cwd=self.project.project_file.parent)

    def _clean_file(self, source: Path):
        """Clean an artifact."""
        artifacts, command = self._get_artifacts(source)
        for artifact in artifacts:
            remove_path(artifact)
            self._clean_file(artifact)  # Recurse for QML (json->qmltypes)

    def clean(self):
        """Clean build artifacts."""
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file).clean()
        for file in self.project.files:
            self._clean_file(file)
        if self._qml_module_dir and self._qml_module_dir.is_dir():
            remove_path(self._qml_module_dir)
            # In case of a dir hierarchy ("a.b" -> a/b), determine and delete
            # the root directory
            if self._qml_module_dir.parent != self.project.project_file.parent:
                project_dir_parts = len(self.project.project_file.parent.parts)
                first_module_dir = self._qml_module_dir.parts[project_dir_parts]
                remove_path(self.project.project_file.parent / first_module_dir)

    def _qmllint(self):
        """Helper for running qmllint on .qml files (non-recursive)."""
        if not self.project.qml_files:
            print(f"{self.project.project_file.name}: No QML files found", file=sys.stderr)
            return

        cmd = [QMLLINT_CMD]
        if self._qml_dir_file:
            cmd.extend(["-i", os.fspath(self._qml_dir_file)])
        for f in self.project.qml_files:
            cmd.append(os.fspath(f))
        run_command(cmd, cwd=self.project.project_file.parent, ignore_fail=True)

    def qmllint(self):
        """Run qmllint on .qml files."""
        self.build()
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file)._qmllint()
        self._qmllint()

    def deploy(self):
        """Deploys the application"""
        cmd = [DEPLOY_CMD]
        cmd.extend([str(self.project.main_file), "-f"])
        run_command(cmd, cwd=self.project.project_file.parent)

    def lupdate(self):
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file).lupdate()

        if not self.project.ts_files:
            print(f"{self.project.project_file.name}: No .ts file found.",
                  file=sys.stderr)
            return

        source_files = self.project.python_files + self.project.ui_files
        cmd_prefix = [LUPDATE_CMD] + [p.name for p in source_files]
        cmd_prefix.append("-ts")
        for ts_file in self.project.ts_files:
            if requires_rebuild(source_files, ts_file):
                cmd = cmd_prefix
                cmd.append(ts_file.name)
                run_command(cmd, cwd=self.project.project_file.parent)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Only print commands")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild")
    parser.add_argument("--qml-module", "-Q", action="store_true",
                        help="Perform check for QML module")
    mode_choices = ["build", "run", "clean", "qmllint", "deploy", "lupdate"]
    mode_choices.extend(NEW_PROJECT_TYPES.keys())
    parser.add_argument("mode", choices=mode_choices, default="build",
                        type=str, help=MODE_HELP)
    parser.add_argument("file", help="Project file", nargs="?", type=str)

    options = parser.parse_args()
    cl_options = ClOptions(dry_run=options.dry_run, quiet=options.quiet, force=options.force,
                           qml_module=options.qml_module)

    mode = options.mode

    new_project_type = NEW_PROJECT_TYPES.get(mode)
    if new_project_type:
        if not options.file:
            print(f"{mode} requires a directory name.", file=sys.stderr)
            sys.exit(1)
        sys.exit(new_project(options.file, new_project_type))

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
    elif mode == "lupdate":
        project.lupdate()
    else:
        print(f"Invalid mode {mode}", file=sys.stderr)
        sys.exit(1)
