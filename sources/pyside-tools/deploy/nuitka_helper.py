# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import sys
from pathlib import Path
from typing import List

from . import run_command


class Nuitka:
    """
    Wrapper class around the nuitka executable, enabling its usage through python code
    """

    def __init__(self, nuitka):
        self.nuitka = nuitka

    def create_executable(
        self, source_file: Path, extra_args: str, qml_files: List[Path], dry_run: bool
    ):
        extra_args = extra_args.split()
        qml_args = []
        if qml_files:
            # this includes "all" the plugins
            # FIXME: adding the "qml" plugin is equivalent to "all" because of dependencies
            # Ideally it should only add the specific qml plugins. eg: quick window, quick controls
            qml_args.append("--include-qt-plugins=all")
            qml_args.extend(
                [f"--include-data-files={qml_file}=./{qml_file.name}" for qml_file in qml_files]
            )

        output_dir = source_file.parent / "deployment"
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            print("[DEPLOY] Running Nuitka")
        command = self.nuitka + [
            os.fspath(source_file),
            "--follow-imports",
            "--onefile",
            "--enable-plugin=pyside6",
            f"--output-dir={output_dir}",
        ]
        command.extend(extra_args + qml_args)

        if sys.platform == "linux":
            linux_icon = str(Path(__file__).parent / "pyside_icon.jpg")
            command.append(f"--linux-onefile-icon={linux_icon}")

        run_command(command=command, dry_run=dry_run)
