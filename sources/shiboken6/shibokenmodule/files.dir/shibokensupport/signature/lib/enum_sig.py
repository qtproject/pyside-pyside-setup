#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
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

"""
enum_sig.py

Enumerate all signatures of a class.

This module separates the enumeration process from the formatting.
It is not easy to adhere to this protocol, but in the end, it paid off
by producing a lot of clarity.
"""

import inspect
import sys
import types
import typing
from shibokensupport.signature import get_signature as get_sig
from shibokensupport.signature.layout import create_signature


"""
PYSIDE-1599: Making sure that pyi files always are tested.

A new problem popped up when supporting true properties:
When there exists an item named "property", then we cannot use
the builtin `property` as decorator, but need to prefix it with "builtins".

We scan for such a name in a class, and if there should a property be
declared in the same class, we use `builtins.property` in the class and
all sub-classes. The same consideration holds for "overload".
"""


class ExactEnumerator(object):
    """
    ExactEnumerator enumerates all signatures in a module as they are.

    This class is used for generating complete listings of all signatures.
    An appropriate formatter should be supplied, if printable output
    is desired.
    """

    def __init__(self, formatter, result_type=dict):
        global EnumMeta
        try:
            # Lazy import
            from PySide6.QtCore import Qt
            EnumMeta = type(Qt.Key)
        except ImportError:
            EnumMeta = None

        self.fmt = formatter
        self.result_type = result_type
        self.fmt.level = 0
        self.fmt.is_method = self.is_method
        self.collision_candidates = {"property", "overload"}

    def is_method(self):
        """
        Is this function a method?
        We check if it is a simple function.
        """
        tp = type(self.func)
        return tp not in (types.BuiltinFunctionType, types.FunctionType)

    def section(self):
        if hasattr(self.fmt, "section"):
            self.fmt.section()

    def module(self, mod_name):
        __import__(mod_name)
        self.fmt.mod_name = mod_name
        with self.fmt.module(mod_name):
            module = sys.modules[mod_name]
            members = inspect.getmembers(module, inspect.isclass)
            functions = inspect.getmembers(module, inspect.isroutine)
            ret = self.result_type()
            self.fmt.class_name = None
            for class_name, klass in members:
                self.collision_track = set()
                ret.update(self.klass(class_name, klass))
            if len(members):
                self.section()
            for func_name, func in functions:
                ret.update(self.function(func_name, func))
            if len(functions):
                self.section()
            return ret

    def klass(self, class_name, klass):
        ret = self.result_type()
        if "<" in class_name:
            # This is happening in QtQuick for some reason:
            ## class QSharedPointer<QQuickItemGrabResult >:
            # We simply skip over this class.
            return ret
        bases_list = []
        for base in klass.__bases__:
            name = base.__qualname__
            if name not in ("object", "property", "type"):
                name = base.__module__ + "." + name
            bases_list.append(name)
        bases_str = ', '.join(bases_list)
        class_str = f"{class_name}({bases_str})"
        # class_members = inspect.getmembers(klass)
        # gives us also the inherited things.
        class_members = sorted(list(klass.__dict__.items()))
        subclasses = []
        functions = []
        enums = []
        properties = []

        for thing_name, thing in class_members:
            if inspect.isclass(thing):
                subclass_name = ".".join((class_name, thing_name))
                subclasses.append((subclass_name, thing))
            elif inspect.isroutine(thing):
                func_name = thing_name.split(".")[0]   # remove ".overload"
                functions.append((func_name, thing))
            elif type(type(thing)) is EnumMeta:
                # take the real enum name, not what is in the dict
                enums.append((thing_name, type(thing).__qualname__, thing))
            elif isinstance(thing, property):
                properties.append((thing_name, thing))

            if thing_name in self.collision_candidates:
                self.collision_track.add(thing_name)

        init_signature = getattr(klass, "__signature__", None)
        enums.sort(key=lambda tup: tup[1 : 3])  # sort by class then enum value

        # We want to handle functions and properties together.
        func_prop = sorted(functions + properties, key=lambda tup: tup[0])

        # find out how many functions create a signature
        sigs = list(_ for _ in functions if hasattr(_[1], "__signature__") and _[1].__signature__)
        self.fmt.have_body = bool(subclasses or sigs or properties or enums or init_signature)

        with self.fmt.klass(class_name, class_str):
            self.fmt.level += 1
            self.fmt.class_name = class_name
            if hasattr(self.fmt, "enum"):
                # this is an optional feature
                if len(enums):
                    self.section()
                for enum_name, enum_class_name, value in enums:
                    with self.fmt.enum(enum_class_name, enum_name, int(value)):
                        pass
            if len(subclasses):
                self.section()
            for subclass_name, subclass in subclasses:
                save = self.collision_track.copy()
                ret.update(self.klass(subclass_name, subclass))
                self.collision_track = save
                self.fmt.class_name = class_name
            if len(subclasses):
                self.section()
            ret.update(self.function("__init__", klass))
            for func_name, func in func_prop:
                if func_name != "__init__":
                    if isinstance(func, property):
                        ret.update(self.fproperty(func_name, func))
                    else:
                        ret.update(self.function(func_name, func))
            self.fmt.level -= 1
            if len(func_prop):
                self.section()
        return ret

    @staticmethod
    def get_signature(func):
        return func.__signature__

    def function(self, func_name, func, decorator=None):
        self.func = func    # for is_method()
        ret = self.result_type()
        if decorator in self.collision_track:
            decorator = f"builtins.{decorator}"
        signature = self.get_signature(func, decorator)
        if signature is not None:
            with self.fmt.function(func_name, signature, decorator) as key:
                ret[key] = signature
        del self.func
        return ret

    def fproperty(self, prop_name, prop):
        ret = self.function(prop_name, prop.fget, type(prop).__qualname__)
        if prop.fset:
            ret.update(self.function(prop_name, prop.fset, f"{prop_name}.setter"))
        if prop.fdel:
            ret.update(self.function(prop_name, prop.fdel, f"{prop_name}.deleter"))
        return ret


def stringify(signature):
    if isinstance(signature, list):
        # remove duplicates which still sometimes occour:
        ret = set(stringify(sig) for sig in signature)
        return sorted(ret) if len(ret) > 1 else list(ret)[0]
    return tuple(str(pv) for pv in signature.parameters.values())


class SimplifyingEnumerator(ExactEnumerator):
    """
    SimplifyingEnumerator enumerates all signatures in a module filtered.

    There are no default values, no variable
    names and no self parameter. Only types are present after simplification.
    The functions 'next' resp. '__next__' are removed
    to make the output identical for Python 2 and 3.
    An appropriate formatter should be supplied, if printable output
    is desired.
    """

    def function(self, func_name, func):
        ret = self.result_type()
        signature = get_sig(func, 'existence')
        sig = stringify(signature) if signature is not None else None
        if sig is not None and func_name not in ("next", "__next__", "__div__"):
            with self.fmt.function(func_name, sig) as key:
                ret[key] = sig
        return ret


class HintingEnumerator(ExactEnumerator):
    """
    HintingEnumerator enumerates all signatures in a module slightly changed.

    This class is used for generating complete listings of all signatures for
    hinting stubs. Only default values are replaced by "...".
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # We need to provide default signatures for class properties.
        cls_param = inspect.Parameter("cls", inspect._POSITIONAL_OR_KEYWORD)
        set_param = inspect.Parameter("arg_1", inspect._POSITIONAL_OR_KEYWORD, annotation=object)
        self.getter_sig = inspect.Signature([cls_param], return_annotation=object)
        self.setter_sig = inspect.Signature([cls_param, set_param])
        self.deleter_sig = inspect.Signature([cls_param])

    def get_signature(self, func, decorator=None):
        # Class properties don't have signature support (yet).
        # In that case, produce a fake one.
        sig = get_sig(func, "hintingstub")
        if not sig:
            if decorator:
                if decorator.endswith(".setter"):
                    sig = self.setter_sig
                elif decorator.endswith(".deleter"):
                    sig = self.deleter_sig
                else:
                    sig = self.getter_sig
        return sig
