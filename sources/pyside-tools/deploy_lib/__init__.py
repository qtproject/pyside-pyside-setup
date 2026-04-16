# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
import logging
import sys
from pathlib import Path
from textwrap import dedent

MAJOR_VERSION = 6

if sys.platform == "win32":
    IMAGE_FORMAT = ".ico"
    EXE_FORMAT = ".exe"
elif sys.platform == "darwin":
    IMAGE_FORMAT = ".icns"
    EXE_FORMAT = ".app"
else:
    IMAGE_FORMAT = ".jpg"
    EXE_FORMAT = ".bin"

DEFAULT_APP_ICON = str((Path(__file__).parent / f"pyside_icon{IMAGE_FORMAT}").resolve())
DEFAULT_IGNORE_DIRS = {"site-packages", "deployment", ".git", ".qtcreator", "build", "dist",
                       "tests", "doc", "docs", "examples", ".vscode", "__pycache__"}

IMPORT_WARNING_PYSIDE = (f"[DEPLOY] Found 'import PySide6' in file {0}"
                         ". Use 'from PySide6 import <module>' or pass the module"
                         " needed using --extra-modules command line argument")
HELP_EXTRA_IGNORE_DIRS = dedent("""
                                Comma-separated directory names inside the project dir. These
                                directories will be skipped when searching for Python files
                                relevant to the project.

                                Example usage: --extra-ignore-dirs=doc,translations
                                """)

HELP_EXTRA_MODULES = dedent("""
                            Comma-separated list of Qt modules to be added to the application,
                            in case they are not found automatically.

                            This occurs when you have 'import PySide6' in your code instead
                            'from PySide6 import <module>'. The module name is specified
                            by either omitting the prefix of Qt or including it.

                            Example usage 1: --extra-modules=Network,Svg
                            Example usage 2: --extra-modules=QtNetwork,QtSvg
                            """)

HELP_MODE = dedent("""
                   The mode in which the application is deployed. The options are: onefile,
                   standalone. The default value is onefile.

                   This options translates to the mode Nuitka uses to create the executable.

                   macOS by default uses the --standalone option.
                   """)

# plugins to be removed from the --include-qt-plugins option because these plugins
# don't exist in site-package under PySide6/Qt/plugins
PLUGINS_TO_REMOVE = ["accessiblebridge", "platforms/darwin", "networkaccess",
                     "scenegraph", "wayland-inputdevice-integration"]


def get_all_pyside_modules():
    """
    Returns all the modules installed with PySide6
    """
    import PySide6
    # They all start with `Qt` as the prefix. Removing this prefix and getting the actual
    # module name
    return [module[2:] for module in PySide6.__all__]


def add_deploy_arguments(parser, include_main_file=True):
    """Add pyside6-deploy arguments to an argparse parser.

    When include_main_file is False, the positional main_file argument is omitted
    (used when called from pyside6-project where the main file comes from the project file).
    """

    parser.add_argument("-c", "--config-file", type=lambda p: Path(p).absolute(),
                        default=None,
                        help="Path to the .spec config file")

    if include_main_file:
        parser.add_argument(
            type=lambda p: Path(p).absolute(),
            help="Path to main python file", nargs="?", dest="main_file",
            default=None if config_option_exists() else Path.cwd() / "main.py")

    parser.add_argument(
        "--init", action="store_true",
        help="Create pysidedeploy.spec file, if it doesn't already exists")

    parser.add_argument(
        "-v", "--verbose", help="Run in verbose mode", action="store_const",
        dest="loglevel", const=logging.INFO)

    parser.add_argument("--dry-run", action="store_true", help="Show the commands to be run")

    parser.add_argument(
        "--keep-deployment-files", action="store_true",
        help="Keep the generated deployment files generated")

    parser.add_argument("-f", "--force", action="store_true", help="Force all input prompts")

    parser.add_argument("--name", type=str, help="Application name")

    parser.add_argument("--extra-ignore-dirs", type=str, help=HELP_EXTRA_IGNORE_DIRS)

    parser.add_argument("--extra-modules", type=str, help=HELP_EXTRA_MODULES)

    parser.add_argument("--mode", choices=["onefile", "standalone"], default=None,
                        help=HELP_MODE)


from .commands import (  # noqa: F401, E402
    run_command,
    run_qmlimportscanner,
)

from .dependency_util import (  # noqa: F401, E402
    find_pyside_modules,
    find_permission_categories,
    QtDependencyReader,
)

from .nuitka_helper import (  # noqa: F401, E402
    Nuitka,
)

from .config import (  # noqa: F401, E402
    BaseConfig,
    Config,
    DesktopConfig,
)

from .python_helper import (  # noqa: F401, E402
    PythonExecutable,
)

from .deploy_util import (  # noqa: F401, E402
    cleanup,
    finalize,
    create_config_file,
    config_option_exists,
)
