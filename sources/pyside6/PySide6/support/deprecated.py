# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
deprecated.py

This module contains deprecated things that are removed from the interface.
They are implemented in Python again, together with a deprecation warning.

Functions that are to be called for
    PySide6.<module> must be named
    fix_for_<module> .

Note that this fixing code is run after all initializations, but before the
import is finished. But that is no problem since the module is passed in.
"""

import warnings
from textwrap import dedent


class PySideDeprecationWarningRemovedInQt6(Warning):
    pass


def constData(self):
    cls = self.__class__
    name = cls.__qualname__
    warnings.warn(dedent(f"""
        {name}.constData is unpythonic and will be removed in Qt For Python 6.0 .
        Please use {name}.data instead."""), PySideDeprecationWarningRemovedInQt6, stacklevel=2)
    return cls.data(self)


# No longer needed but kept for reference.
def _unused_fix_for_QtGui(QtGui):
    for name, cls in QtGui.__dict__.items():
        if name.startswith("QMatrix") and "data" in cls.__dict__:
            cls.constData = constData

# eof
