# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from .android_helper import (create_recipe, extract_and_copy_jar, get_wheel_android_arch,
                             AndroidData, get_llvm_readobj, find_lib_dependencies,
                             find_qtlibs_in_wheel)
from .buildozer import Buildozer
