# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import atexit
from pathlib import Path

# FIXME: Remove this idea of creating main_patch.py once the corresponding changes are
#        made in Design Studio main.py file:
#     if '__compiled__' in globals(): #nuitka
#        app_dir = Path(__file__).parent
#     else:
#        app_dir = Path(__file__).parent.parent


class DesignStudio:
    """
    Class to handle Design Studio projects
    """

    def __init__(self, main_file: Path):
        self.ds_project_dir = main_file.parent.parent
        self.current_main_file = main_file
        self.new_main_file = main_file.parent / 'main_patch.py'
        self._create_new_main_file()
        atexit.register(self._delete_main_patch_file)

    def _create_new_main_file(self):
        # read the content of main file
        content = ""
        with open(self.current_main_file, 'r', encoding='utf-8') as main_file:
            content = main_file.read()

        # replace app_dir
        content = content.replace("app_dir = Path(__file__).parent.parent",  # old value
                                  "app_dir = Path(__file__).parent")  # new value

        # write the content to new main file
        with open(self.new_main_file, 'w', encoding="utf-8") as main_file:
            main_file.write(content)

    def _delete_main_patch_file(self):
        if self.new_main_file.exists():
            logging.info(f"[DEPLOY] Removing {self.new_main_file}")
            self.new_main_file.unlink()

    @staticmethod
    def isDSProject(main_file: Path) -> bool:
        return (main_file.parent / 'autogen/settings.py').exists()

    @property
    def project_dir(self) -> str:
        return self.ds_project_dir

    @property
    def ds_source_file(self) -> Path:
        return self.new_main_file
