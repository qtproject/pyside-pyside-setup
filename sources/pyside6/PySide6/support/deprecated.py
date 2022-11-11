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

PYSIDE-1735: This is also used now for missing other functions (overwriting __or__
             in Qt.(Keyboard)Modifier).
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

# PYSIDE-1735: Fix for a special enum function
def fix_for_QtCore(QtCore):
    from enum import Flag
    Qt = QtCore.Qt
    flag_or = Flag.__or__

    def func_or(self, other):
        if isinstance(self, Flag) and isinstance(other, Flag):
            # this is normal or-ing flags together
            return Qt.KeyboardModifier(self.value | other.value)
        return QtCore.QKeyCombination(self, other)

    def func_add(self, other):
        warnings.warn(dedent(f"""
            The "+" operator is deprecated in Qt For Python 6.0 .
            Please use "|" instead."""), PySideDeprecationWarningRemovedInQt6, stacklevel=2)
        return func_or(self, other)

    Qt.KeyboardModifier.__or__ = func_or
    Qt.KeyboardModifier.__ror__ = func_or
    Qt.Modifier.__or__ = func_or
    Qt.Modifier.__ror__ = func_or
    Qt.KeyboardModifier.__add__ = func_add
    Qt.KeyboardModifier.__radd__ = func_add
    Qt.Modifier.__add__ = func_add
    Qt.Modifier.__radd__ = func_add

# eof
