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
        # plugins to ignore. The sensible plugins are include by default by Nuitka for PySide6
        # application deployment
        self.qt_plugins_to_ignore = ["imageformats",  # being Nuitka `sensible`` plugins
                                     "iconengines",
                                     "mediaservice",
                                     "printsupport",
                                     "platforms",
                                     "platformthemes",
                                     "styles",
                                     "wayland-shell-integration",
                                     "wayland-decoration-client",
                                     "wayland-graphics-integration-client",
                                     "egldeviceintegrations",
                                     "xcbglintegrations",
                                     "tls",  # end Nuitka `sensible` plugins
                                     "generic"  # plugins that error with Nuitka
                                     ]

        # .webp are considered to be dlls by Nuitka instead of data files causing
        # the packaging to fail
        # https://github.com/Nuitka/Nuitka/issues/2854
        # TODO: Remove .webp when the issue is fixed
        self.files_to_ignore = [".cpp.o", ".qsb", ".webp"]

    @staticmethod
    def icon_option():
        if sys.platform == "linux":
            return "--linux-icon"
        elif sys.platform == "win32":
            return "--windows-icon-from-ico"
        else:
            return "--macos-app-icon"

    def create_executable(self, source_file: Path, extra_args: str, qml_files: List[Path],
                          qt_plugins: List[str], excluded_qml_plugins: List[str], icon: str,
                          dry_run: bool, permissions: List[str]):
        qt_plugins = [plugin for plugin in qt_plugins if plugin not in self.qt_plugins_to_ignore]
        extra_args = extra_args.split()

        if sys.platform == "darwin":
            # create an app bundle
            extra_args.extend(["--standalone", "--macos-create-app-bundle"])
            permission_pattern = "--macos-app-protected-resource={permission}"
            for permission in permissions:
                extra_args.append(permission_pattern.format(permission=permission))
        else:
            extra_args.append("--onefile")

        qml_args = []
        if qml_files:
            # This will generate options for each file using:
            #     --include-data-files=ABSOLUTE_PATH_TO_FILE=RELATIVE_PATH_TO ROOT
            # for each file. This will preserve the directory structure of QML resources.
            qml_args.extend(
                [f"--include-data-files={qml_file.resolve()}="
                 f"./{qml_file.resolve().relative_to(source_file.parent)}"
                 for qml_file in qml_files]
            )
            # add qml plugin. The `qml`` plugin name is not present in the module json files shipped
            # with Qt and hence not in `qt_plugins``. However, Nuitka uses the 'qml' plugin name to
            # include the necessary qml plugins. There we have to add it explicitly for a qml
            # application
            qt_plugins.append("qml")

            if excluded_qml_plugins:
                prefix = "lib" if sys.platform != "win32" else ""
                for plugin in excluded_qml_plugins:
                    dll_name = plugin.replace("Qt", f"Qt{MAJOR_VERSION}")
                    qml_args.append(f"--noinclude-dlls={prefix}{dll_name}*")

            # Exclude .qen json files from QtQuickEffectMaker
            # These files are not relevant for PySide6 applications
            qml_args.append("--noinclude-dlls=*/qml/QtQuickEffectMaker/*")

        # Exclude files that cannot be processed by Nuitka
        for file in self.files_to_ignore:
            extra_args.append(f"--noinclude-dlls=*{file}")

        output_dir = source_file.parent / "deployment"
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info("[DEPLOY] Running Nuitka")
        command = self.nuitka + [
            os.fspath(source_file),
            "--follow-imports",
            "--enable-plugin=pyside6",
            f"--output-dir={output_dir}",
        ]

        command.extend(extra_args + qml_args)
        command.append(f"{self.__class__.icon_option()}={icon}")
        if qt_plugins:
            # sort qt_plugins so that the result is definitive when testing
            qt_plugins.sort()
            qt_plugins_str = ",".join(qt_plugins)
            command.append(f"--include-qt-plugins={qt_plugins_str}")

        command_str, _ = run_command(command=command, dry_run=dry_run)
        return command_str
