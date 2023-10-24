# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

# maps instruction set to Android platform names
platform_map = {"aarch64": "arm64-v8a",
                "armv7a": "armeabi-v7a",
                "i686": "x86",
                "x86_64": "x86_64",
                "arm64-v8a": "arm64-v8a",
                "armeabi-v7a": "armeabi-v7a",
                "x86": "x86"}

from .android_helper import (create_recipe, extract_and_copy_jar, get_wheel_android_arch,
                             AndroidData, get_llvm_readobj, find_lib_dependencies,
                             find_qtlibs_in_wheel)
from .android_config import AndroidConfig
