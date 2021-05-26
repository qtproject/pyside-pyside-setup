# This Python file uses the following encoding: utf-8
#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

from __future__ import annotations

"""
This file contains the exact signatures for all functions in module
Shiboken, except for defaults which are replaced by "...".
"""

# Module `Shiboken`

from shiboken6 import Shiboken


class Object(object):

    def __init__(self) -> None: ...


class VoidPtr(object): ...


def _unpickle_enum(arg__1: object, arg__2: object) -> object: ...
def createdByPython(arg__1: object) -> bool: ...
def delete(arg__1: object) -> None: ...
def dump(arg__1: object) -> object: ...
def getAllValidWrappers() -> object: ...
def getCppPointer(arg__1: object) -> object: ...
def invalidate(arg__1: object) -> None: ...
def isValid(arg__1: object) -> bool: ...
def ownedByPython(arg__1: object) -> bool: ...
def wrapInstance(arg__1: int, arg__2: type) -> object: ...


# eof
