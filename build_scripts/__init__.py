# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
from pathlib import Path

PYSIDE = 'pyside6'
PYSIDE_MODULE = 'PySide6'
SHIBOKEN = 'shiboken6'
SHIBOKEN_GENERATOR = 'shiboken6_generator'

PYSIDE_PYTHON_TOOLS = ["metaobjectdump",
                       "deploy",
                       "android_deploy",
                       "ios_deploy",
                       "project",
                       "qml",
                       "qtpy2cpp",
                       "genpyi"]

PYSIDE_UNIX_BIN_TOOLS = ["lupdate",
                         "lrelease",
                         "qmllint",
                         "qmlformat",
                         "qmlls",
                         "qsb",
                         "balsam",
                         "balsamui",
                         "svgtoqml",]

# tools that are bundled as .app in macOS, but are normal executables in Linux and Windows
PYSIDE_UNIX_BUNDLED_TOOLS = ["assistant",
                             "designer",
                             "linguist"]

PYSIDE_LINUX_BIN_TOOLS = PYSIDE_UNIX_BIN_TOOLS + PYSIDE_UNIX_BUNDLED_TOOLS

PYSIDE_UNIX_LIBEXEC_TOOLS = ["uic",
                             "rcc",
                             "qmltyperegistrar",
                             "qmlimportscanner",
                             "qmlcachegen"]

# all Qt tools are in 'bin' folder in Windows
PYSIDE_WINDOWS_BIN_TOOLS = PYSIDE_UNIX_LIBEXEC_TOOLS + PYSIDE_LINUX_BIN_TOOLS

PYSIDE_MULTIMEDIA_LIBS = ["avcodec", "avformat", "avutil",
                          "swresample", "swscale"]

PYPROJECT_PATH = Path(__file__).parents[1] / "wheel_artifacts" / "pyproject.toml.base"
