# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import sys
from pathlib import Path

MAJOR_VERSION = 6

if sys.platform == "win32":
    IMAGE_FORMAT = ".ico"
    EXE_FORMAT = ".exe"
elif sys.platform == "darwin":
    IMAGE_FORMAT = ".icns"
    EXE_FORMAT = ".bin"
else:
    IMAGE_FORMAT = ".jpg"
    EXE_FORMAT = ".bin"

DEFAULT_APP_ICON = str((Path(__file__).parent / f"pyside_icon{IMAGE_FORMAT}").resolve())

from .commands import run_command
from .nuitka_helper import Nuitka
from .python_helper import PythonExecutable, find_pyside_modules
from .config import BaseConfig, Config
from .deploy_util import (cleanup, finalize, create_config_file, setup_python,
                          install_python_dependencies, config_option_exists)
