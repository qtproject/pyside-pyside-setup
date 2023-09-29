# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import sys

MAJOR_VERSION = 6
EXE_FORMAT = ".exe" if sys.platform == "win32" else ".bin"

from .commands import run_command
from .config import BaseConfig, Config
from .nuitka_helper import Nuitka
from .deploy_util import (cleanup, config_option_exists, finalize, get_config,
                          install_python_dependencies, setup_python)
from .python_helper import PythonExecutable, find_pyside_modules
