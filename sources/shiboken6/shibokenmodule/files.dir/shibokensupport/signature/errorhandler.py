# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
errorhandler.py

This module handles the TypeError messages which were previously
produced by the generated C code.

This version is at least consistent with the signatures, which
are created by the same module.

Experimentally, we are trying to guess those errors which are
just the wrong number of elements in an iterator.
At the moment, it is unclear whether the information given is
enough to produce a useful ValueError.

This matter will be improved in a later version.
"""

import collections.abc
import inspect
import sys
import typing

from shibokensupport.signature import get_signature
from shibokensupport.signature.mapping import update_mapping, namespace
from textwrap import dedent


def qt_isinstance(inst, the_type):
    if the_type == float:
        # Qt thinks differently about int and float - simply keep it.
        return isinstance(inst, int) or isinstance(inst, float)
    if the_type.__module__ == "typing":
        if the_type is typing.Any:
            return True
        if the_type.__origin__ is typing.Union:
            return any(qt_isinstance(inst, _) for _ in the_type.__args__)
        if the_type.__origin__ in (collections.abc.Sequence,
                                   collections.abc.Iterable):
            try:
                return all(qt_isinstance(_, the_type.__args__[0]) for _ in inst)
            except TypeError:
                return False
    try:
        return isinstance(inst, the_type)
    except TypeError as e:
        print(f"FIXME qt_isinstance({inst}, {the_type}):", e)
        return False


def matched_type(args, sigs):
    for sig in sigs:
        params = list(sig.parameters.values())
        if len(args) > len(params):
            continue
        if len(args) < len(params):
            k = len(args)
            if params[k].default is params[k].empty:
                # this is a necessary parameter, so it fails.
                continue
        if all(qt_isinstance(arg, param.annotation) for arg, param in zip(args, params)):
            return sig
    return None


def seterror_argument(args, func_name, info):
    func = None
    try:
        func = eval(func_name, namespace)
    except Exception as e:
        msg = f"Error evaluating `{func_name}`: {e}"
        return type(e), msg
    if info and type(info) is str:
        err = TypeError
        if info == "<":
            msg = f"{func_name}(): not enough arguments"
        elif info == "0":
           msg = (f"{func_name}(): not enough arguments. "
                  "Note: keyword arguments are only supported for optional parameters.")
        elif info == ">":
            msg = f"{func_name}(): too many arguments"
        elif info.isalnum():
            msg = f"{func_name}(): got multiple values for keyword argument '{info}'"
        else:
            msg = f"{func_name}(): {info}"
            err = AttributeError
        return err, msg
    if isinstance(info, Exception):
        # PYSIDE-2230: Python 3.12 seems to always do normalization.
        err = type(info)
        info = info.args[0]
        msg = f"{func_name}(): {info}"
        return err, msg
    if info and type(info) is dict:
        msg = f"{func_name}(): unsupported keyword '{tuple(info)[0]}'"
        return AttributeError, msg
    sigs = get_signature(func, "typeerror")
    if not sigs:
        msg = f"{func_name}({args}) is wrong (missing signature)"
        return TypeError, msg
    if type(sigs) != list:
        sigs = [sigs]
    if type(args) != tuple:
        args = (args,)
    # temp!
    found = matched_type(args, sigs)
    if found:
        msg = dedent(f"""
            {func_name!r} called with wrong argument values:
              {func_name}{args}
            Found signature:
              {func_name}{found}
            """).strip()
        return ValueError, msg
    type_str = ", ".join(type(arg).__name__ for arg in args)
    msg = dedent(f"""
        {func_name!r} called with wrong argument types:
          {func_name}({type_str})
        Supported signatures:
        """).strip()
    for sig in sigs:
        msg += f"\n  {func_name}{sig}"
    # We don't raise the error here, to avoid the loader in the traceback.
    return TypeError, msg


def check_string_type(s):
    return isinstance(s, str)


def make_helptext(func):
    existing_doc = func.__doc__
    if existing_doc is None and hasattr(func, "__dict__"):
        existing_doc = func.__dict__.get("__doc__")
    sigs = get_signature(func)
    if not sigs:
        return existing_doc
    if type(sigs) != list:
        sigs = [sigs]
    try:
        func_name = func.__name__
    except AttributeError:
        func_name = func.__func__.__name__
    sigtext = "\n".join(func_name + str(sig) for sig in sigs)
    msg = f"{sigtext}\n\n{existing_doc}" if check_string_type(existing_doc) else sigtext
    return msg

# end of file
