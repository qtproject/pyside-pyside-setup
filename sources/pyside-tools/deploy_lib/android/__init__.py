# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
from pathlib import Path

# maps instruction set to Android platform names
platform_map = {"aarch64": "arm64-v8a",
                "x86_64": "x86_64",
                "arm64-v8a": "arm64-v8a"}

ANDROID_DEPLOY_CACHE = Path.home() / ".pyside6_android_deploy"

from .android_helper import (create_recipe, extract_and_copy_jar, get_wheel_android_arch,
                             AndroidData, get_llvm_readobj, find_lib_dependencies,
                             find_qtlibs_in_wheel, safe_extractall)
from .android_config import AndroidConfig
