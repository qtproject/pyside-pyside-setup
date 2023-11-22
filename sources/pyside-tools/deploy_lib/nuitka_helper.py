# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import os
import sys
from pathlib import Path
from typing import List

from . import MAJOR_VERSION, run_command


class Nuitka:
    """
    Wrapper class around the nuitka executable, enabling its usage through python code
    """

    def __init__(self, nuitka):
        self.nuitka = nuitka

    def create_executable(self, source_file: Path, extra_args: str, qml_files: List[Path],
                          excluded_qml_plugins, dry_run: bool):
        extra_args = extra_args.split()
        qml_args = []
        if qml_files:
            qml_args.append("--include-qt-plugins=all")
            # This will generate options for each file using:
            #     --include-data-files=ABSOLUTE_PATH_TO_FILE=RELATIVE_PATH_TO ROOT
            # for each file. This will preserve the directory structure of QML resources.
            qml_args.extend(
                [f"--include-data-files={qml_file.resolve()}="
                 f"./{qml_file.resolve().relative_to(source_file.parent)}"
                 for qml_file in qml_files]
            )

            if excluded_qml_plugins:
                prefix = "lib" if sys.platform != "win32" else ""
                for plugin in excluded_qml_plugins:
                    dll_name = plugin.replace("Qt", f"Qt{MAJOR_VERSION}")
                    qml_args.append(f"--noinclude-dlls={prefix}{dll_name}*")

        output_dir = source_file.parent / "deployment"
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info("[DEPLOY] Running Nuitka")
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

        command_str, _ = run_command(command=command, dry_run=dry_run)
        return command_str
