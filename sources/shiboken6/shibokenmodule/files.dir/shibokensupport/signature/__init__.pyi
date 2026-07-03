# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:default

import typing
import inspect

from . import mapping
from . import lib
from . import layout

__all__ = ["get_signature", "make_snake_case_name", "layout", "mapping", "lib"]

@typing.overload
def get_signature(ob: object, /) -> typing.Union[inspect.Signature, list[inspect.Signature], None]: ...
@typing.overload
def get_signature(ob: object, modifier: str, /) -> typing.Union[inspect.Signature, list[inspect.Signature], None]: ...

def make_snake_case_name(name: str) -> str: ...
