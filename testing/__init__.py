# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
testing/__init__.py

- install an alternative, flushing print
- define command.main as entry point
"""

import builtins
import sys

from . import command

main = command.main

# modify print so that it always flushes
builtins.orig_print = builtins.print


def print_flushed(*args, **kw):
    orig_print(*args, **kw)
    sys.stdout.flush()


builtins.print = print_flushed

print = print_flushed

# We also could use "python -u" to get unbuffered output.
# This method is better since it needs no change of the interface.

# eof
