# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from other import OtherObjectType
from sample import ObjectType


class MyObjectType(ObjectType):
    pass


class MyOtherObjectType(OtherObjectType):
    value = 10


obj = MyObjectType()
