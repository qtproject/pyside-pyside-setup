# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
import os
from pathlib import Path
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter

from project_lib import (QmlProjectData, check_qml_decorators, is_python_file, migrate_pyproject,
                         QMLDIR_FILE, MOD_CMD, METATYPES_JSON_SUFFIX, SHADER_SUFFIXES,
                         TRANSLATION_SUFFIX, requires_rebuild, run_command, remove_path,
                         ProjectData, resolve_valid_project_file, new_project, NewProjectTypes,
                         ClOptions, DesignStudioProject)
from deploy_lib import add_deploy_arguments

DESCRIPTION = """
pyside6-project is a command line tool for creating, building and deploying Qt for Python
applications. It operates on project files which are also used by Qt Creator.

Official documentation:
https://doc.qt.io/qtforpython-6/tools/pyside-project.html
"""

OPERATION_HELP = {
    "build": "Build the project. Compiles resources, UI files, and QML files if existing and "
             "necessary.",
    "run": "Build and run the project.",
    "clean": "Clean build artifacts and generated files from the project directory.",
    "qmllint": "Run the qmllint tool on QML files in the project.",
    "deploy": "Create a deployable package of the application including all dependencies.",
    "lupdate": "Update translation files (.ts) with new strings from source files.",
    "migrate-pyproject": "Migrate a *.pyproject file to pyproject.toml format."
}

UIC_CMD = "pyside6-uic"
RCC_CMD = "pyside6-rcc"
LRELEASE_CMD = "pyside6-lrelease"
LUPDATE_CMD = "pyside6-lupdate"
QMLTYPEREGISTRAR_CMD = "pyside6-qmltyperegistrar"
QMLLINT_CMD = "pyside6-qmllint"
QSB_CMD = "pyside6-qsb"
DEPLOY_CMD = "pyside6-deploy"


def _sort_sources(files: list[Path]) -> list[Path]:
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
        self._qml_module_sources: list[Path] = []
        self._qml_module_dir: Path | None = None
        self._qml_dir_file: Path | None = None
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

    def _get_artifacts(self, file: Path, output_path: Path | None = None) -> \
            tuple[list[Path], list[str] | None]:
        """Return path and command for a file's artifact"""
        if file.suffix == ".ui":  # Qt form files
            py_file = f"{file.parent}/ui_{file.stem}.py"
            cmd = [UIC_CMD]
            cmd.extend(self.project.uic_options)
            cmd.extend([os.fspath(file), "--rc-prefix", "-o", py_file])
            return [Path(py_file)], cmd
        if file.suffix == ".qrc":  # Qt resources
            if not output_path:
                py_file = f"{file.parent}/rc_{file.stem}.py"
            else:
                py_file = str(output_path.resolve())
            cmd = [RCC_CMD]
            cmd.extend(self.project.rcc_options)
            cmd.extend([os.fspath(file), "-o", py_file])
            return [Path(py_file)], cmd
        # generate .qmltypes from sources with Qml decorators
        if file.suffix == ".py" and file in self._qml_module_sources:
            assert self._qml_module_dir
            qml_module_dir = os.fspath(self._qml_module_dir)
            json_file = f"{qml_module_dir}/{file.stem}{METATYPES_JSON_SUFFIX}"
            return [Path(json_file)], [MOD_CMD, "-o", json_file, os.fspath(file)]
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
            return [qmltypes_file, cpp_file], cmd

        if file.name.endswith(TRANSLATION_SUFFIX):
            qm_file = f"{file.parent}/{file.stem}.qm"
            cmd = [LRELEASE_CMD, os.fspath(file), "-qm", qm_file]
            return [Path(qm_file)], cmd

        if file.suffix in SHADER_SUFFIXES:
            qsb_file = f"{file.parent}/{file.stem}.qsb"
            cmd = [QSB_CMD, "-o", qsb_file, os.fspath(file)]
            return [Path(qsb_file)], cmd

        return [], None

    def _regenerate_qmldir(self):
        """Regenerate the 'qmldir' file."""
        if self.cl_options.dry_run or not self._qml_dir_file:
            return
        if self.cl_options.force or requires_rebuild(self._qml_module_sources, self._qml_dir_file):
            with self._qml_dir_file.open("w") as qf:
                qf.write(f"module {self._qml_project_data.import_name}\n")
                for f in self._qml_module_dir.glob("*.qmltypes"):
                    qf.write(f"typeinfo {f.name}\n")

    def _build_file(self, source: Path, output_path: Path | None = None):
        """Build an artifact if necessary."""
        artifacts, command = self._get_artifacts(source, output_path)
        for artifact in artifacts:
            if self.cl_options.force or requires_rebuild([source], artifact):
                run_command(command, cwd=self.project.project_file.parent)
            self._build_file(artifact)  # Recurse for QML (json->qmltypes)

    def build_design_studio_resources(self):
        """
        The resources that need to be compiled are defined in autogen/settings.py
        """
        ds_project = DesignStudioProject(self.project.main_file)
        if (resources_file_path := ds_project.get_resource_file_path()) is None:
            return

        compiled_resources_file_path = ds_project.get_compiled_resources_file_path()
        self._build_file(resources_file_path, compiled_resources_file_path)

    def build(self):
        """Build the whole project"""
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file).build()

        if self._qml_module_dir:
            self._qml_module_dir.mkdir(exist_ok=True, parents=True)

        for file in _sort_sources(self.project.files):
            self._build_file(file)

        if DesignStudioProject.is_ds_project(self.project.main_file):
            self.build_design_studio_resources()

        self._regenerate_qmldir()

    def run(self, args: list) -> int:
        """Runs the project"""
        self.build()
        cmd = [sys.executable, str(self.project.main_file)]
        cmd.extend(args)
        return run_command(cmd, cwd=self.project.project_file.parent)

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

        if DesignStudioProject.is_ds_project(self.project.main_file):
            DesignStudioProject(self.project.main_file).clean()

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

    def deploy(self, args: Namespace):
        """Deploys the application"""
        cmd = [DEPLOY_CMD, str(self.project.main_file)]
        if args.config_file is not None:
            cmd.extend(["-c", str(args.config_file)])
        if args.init:
            cmd.append("--init")
        if args.loglevel is not None:
            cmd.append("--verbose")
        if args.dry_run:
            cmd.append("--dry-run")
        if args.keep_deployment_files:
            cmd.append("--keep-deployment-files")
        if args.force:
            cmd.append("--force")
        if args.name:
            cmd.extend(["--name", args.name])
        if args.extra_ignore_dirs:
            cmd.extend(["--extra-ignore-dirs", args.extra_ignore_dirs])
        if args.extra_modules:
            cmd.extend(["--extra-modules", args.extra_modules])
        if args.mode is not None:
            cmd.extend(["--mode", args.mode])
        run_command(cmd, cwd=self.project.project_file.parent)

    def lupdate(self):
        for sub_project_file in self.project.sub_projects_files:
            Project(project_file=sub_project_file).lupdate()

        if not self.project.ts_files:
            print(f"{self.project.project_file.name}: No .ts file found.",
                  file=sys.stderr)
            return

        source_files = self.project.python_files + self.project.ui_files
        project_dir = self.project.project_file.parent
        cmd_prefix = [LUPDATE_CMD] + [os.fspath(p.relative_to(project_dir)) for p in source_files]
        cmd_prefix.append("-ts")
        for ts_file in self.project.ts_files:
            ts_dir = ts_file.parent
            if not ts_dir.exists():
                ts_dir.mkdir(parents=True, exist_ok=True)
            if requires_rebuild(source_files, ts_file):
                cmd = cmd_prefix
                cmd.append(os.fspath(ts_file))
                run_command(cmd, cwd=project_dir)


def main(args: Namespace):
    mode = args.subcommand
    project_dir = getattr(args, "project_dir", None)
    project_path = getattr(args, "project_path", None)
    legacy_pyproject = getattr(args, "legacy_pyproject", False)
    cl_options = ClOptions(dry_run=args.dry_run, quiet=args.quiet,  # noqa: F841
                           force=args.force, qml_module=args.qml_module)

    if new_project_type := NewProjectTypes.find_by_command(mode):
        if not project_dir:
            print(f"Error creating new project: {mode} requires a directory name or path",
                  file=sys.stderr)
            sys.exit(1)

        project_dir = Path(project_dir)
        try:
            project_dir.resolve()
            project_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, RuntimeError, ValueError):
            print("Invalid project name", file=sys.stderr)
            sys.exit(1)

        sys.exit(new_project(project_dir, new_project_type, legacy_pyproject))

    if mode == "migrate-pyproject":
        sys.exit(migrate_pyproject(project_path))

    try:
        project_file = resolve_valid_project_file(project_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    project = Project(project_file)
    if mode == "build":
        project.build()
    elif mode == "run":
        sys.exit(project.run(args.arguments))
    elif mode == "clean":
        project.clean()
    elif mode == "qmllint":
        project.qmllint()
    elif mode == "deploy":
        project.deploy(args)
    elif mode == "lupdate":
        project.lupdate()
    else:
        print(f"Invalid mode {mode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Only print commands")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild")
    parser.add_argument("--qml-module", "-Q", action="store_true",
                        help="Perform check for QML module")

    # Create subparsers for the two different command branches
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # Add subparser for project creation commands
    for project_type in NewProjectTypes:
        new_parser = subparsers.add_parser(project_type.value.command,
                                           help=project_type.value.description)
        new_parser.add_argument(
            "project_dir", help="Name or location of the new project", nargs="?", type=str)

        new_parser.add_argument(
            "--legacy-pyproject", action="store_true", help="Create a legacy *.pyproject file")

    # Add subparser for project operation commands
    for op_mode, op_help in OPERATION_HELP.items():
        op_parser = subparsers.add_parser(op_mode, help=op_help)
        op_parser.add_argument("project_path", nargs="?", type=str, help="Path to the project file")
        if op_mode == "run":
            op_parser.add_argument('arguments', nargs='*', help="Arguments")
        if op_mode == "deploy":
            add_deploy_arguments(op_parser, include_main_file=False)

    main(parser.parse_args())
