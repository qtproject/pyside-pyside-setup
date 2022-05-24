#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


def objectFullname(t):
    # '__qualname__' for Python 2 does exist for PySide types, only.
    name = getattr(t, "__qualname__", t.__name__)
    module = t.__module__
    if module is None or module == str.__class__.__module__:
        return name
    else:
        return module + '.' + name
