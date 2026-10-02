# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool

from .ios_helper import IOSData, get_wheel_ios_target
from .ios_config import IOSConfig

# PySide6 modules built from PySide sources alone, with no Qt library behind
# them. They are added to the frameworks list without reading a .prl file.
PYSIDE_ONLY_MODULES = {"QtQmlFeatures"}
