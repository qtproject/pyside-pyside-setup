# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from other import *
from sample import *


class MyObjectType(ObjectType):
    pass

class MyOtherObjectType(OtherObjectType):
    value = 10


obj = MyObjectType()
