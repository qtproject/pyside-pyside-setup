# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

PYSIDE = 'pyside6'
PYSIDE_MODULE = 'PySide6'
SHIBOKEN = 'shiboken6'

PYSIDE_PYTHON_TOOLS = ["metaobjectdump",
                       "deploy",
                       "project",
                       "qml",
                       "qtpy2cpp",
                       "genpyi"]
PYSIDE_LINUX_BIN_TOOLS = ["lupdate",
                          "lrelease",
                          "qmllint",
                          "qmlformat",
                          "qmlls",
                          "assistant",
                          "designer",
                          "linguist"]
PYSIDE_LINUX_LIBEXEC_TOOLS = ["uic",
                              "rcc",
                              "qmltyperegistrar",
                              "qmlimportscanner"]
# all Qt tools are in 'bin' folder in Windows
PYSIDE_WINDOWS_BIN_TOOLS = PYSIDE_LINUX_LIBEXEC_TOOLS + PYSIDE_LINUX_BIN_TOOLS
