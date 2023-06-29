#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:COMM$
##
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
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

from shiboken2 import Shiboken


class Object(object):

    def __init__(self) -> None: ...


class VoidPtr(object): ...


def _unpickle_enum(arg__1: object, arg__2: object) -> object: ...
def createdByPython(arg__1: Shiboken.Object) -> bool: ...
def delete(arg__1: Shiboken.Object) -> None: ...
def dump(arg__1: object) -> str: ...
def getAllValidWrappers() -> Shiboken.Object: ...
def getCppPointer(arg__1: Shiboken.Object) -> Shiboken.Object: ...
def invalidate(arg__1: Shiboken.Object) -> None: ...
def isValid(arg__1: object) -> bool: ...
def ownedByPython(arg__1: Shiboken.Object) -> bool: ...
def wrapInstance(arg__1: int, arg__2: type) -> Shiboken.Object: ...


# eof
