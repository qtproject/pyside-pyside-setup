# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

WIDGET_APPLICATION_MODULES = ["Core", "Gui", "Widgets"]
QUICK_APPLICATION_MODULES = ["Core", "Gui", "Widgets", "Network", "OpenGL", "Qml", "Quick",
                             "QuickControls2"]

from .android_helper import (create_recipe, extract_and_copy_jar, get_wheel_android_arch,
                             AndroidData)
from .buildozer import Buildozer
