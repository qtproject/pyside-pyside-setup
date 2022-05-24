# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
testrunner.py

Run ctest on the last build.
See the notes in testing/command.py .
"""

import testing
import testing.blacklist  # just to be sure it's us...

testing.main()
