#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for bug#554'''

import os
import sys
from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *

class Bug554:
    def crash(self):
        class Crasher(ObjectType):
            pass

if __name__ == '__main__':
    bug = Bug554()
    bug.crash()


