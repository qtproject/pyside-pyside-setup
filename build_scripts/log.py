# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging

from enum import Enum

logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
log = logging.getLogger("qtforpython")

class LogLevel(Enum):
    QUIET = 1
    INFO = 2
    VERBOSE = 3

