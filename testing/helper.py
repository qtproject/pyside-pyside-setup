# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""
testing/helper.py

Some tools that do not fit elsewhere.
"""

from pathlib import Path

script_dir = Path(__file__).parent.parent


def decorate(mod_name):
    """
    Write the combination of "modulename_funcname"
    in the Qt-like form "modulename::funcname"
    """
    if "_" not in mod_name or "::" in mod_name:
        return mod_name
    name, rest = mod_name.split("_", 1)
    return f"{name}::{rest}"
