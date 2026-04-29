# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:default
from __future__ import annotations

"""
layout.py

The signature module now has the capability to configure
differently formatted versions of signatures. The default
layout is known from the "__signature__" attribute.

The function "get_signature(ob, modifier=None)" produces the same
signatures by default. By passing different modifiers, you
can select different layouts.

This module configures the different layouts which can be used.
It also implements them in this file. The configurations are
used literally as strings like "signature", "existence", etc.
"""
# flake8: noqa E:731
import inspect
import operator
import sys
import types
import typing

from functools import reduce
from types import SimpleNamespace
from textwrap import dedent
from shibokensupport.signature.mapping import ellipsis, missing_optional_return, PlaceholderType
from shibokensupport.signature.parser import using_snake_case
from shibokensupport.signature import make_snake_case_name
from collections.abc import Sequence, Iterable

DEFAULT_PARAM_KIND = inspect.Parameter.POSITIONAL_ONLY


def formatannotation(annotation, base_module=None):
    if getattr(annotation, '__module__', None) == 'typing':
        return repr(annotation).replace('typing.', '')
    if isinstance(annotation, types.GenericAlias):
        return str(annotation)
    if isinstance(annotation, type):
        if annotation.__module__ in ('builtins', base_module):
            return annotation.__qualname__
        return annotation.__module__ + '.' + annotation.__qualname__
    return repr(annotation)


# PYSIDE-3012: Patching Python < 3.10.1
def install_typing_patch():
    v = sys.version_info[:3]
    if v[1] == 10 and v[2] < 1:
        inspect.formatannotation = formatannotation


install_typing_patch()


class SignatureLayout(SimpleNamespace):
    """
    Configure a signature.

    The layout of signatures can have different layouts which are
    controlled by keyword arguments:

    definition=True         Determines if self will generated.
    defaults=True
    ellipsis=False          Replaces defaults by "...".
    return_annotation=True
    parameter_names=True    False removes names before ":".
    """
    allowed_keys = SimpleNamespace(definition=True,
                                   defaults=True,
                                   ellipsis=False,
                                   return_annotation=True,
                                   parameter_names=True)
    allowed_values = True, False

    def __init__(self, **kwds):
        args = SimpleNamespace(**self.allowed_keys.__dict__)
        args.__dict__.update(kwds)
        self.__dict__.update(args.__dict__)
        err_keys = list(set(self.__dict__) - set(self.allowed_keys.__dict__))
        if err_keys:
            self._attributeerror(err_keys)
        err_values = list(set(self.__dict__.values()) - set(self.allowed_values))
        if err_values:
            self._valueerror(err_values)

    def __setattr__(self, key, value):
        if key not in self.allowed_keys.__dict__:
            self._attributeerror([key])
        if value not in self.allowed_values:
            self._valueerror([value])
        self.__dict__[key] = value

    def _attributeerror(self, err_keys):
        err_keys = ", ".join(err_keys)
        allowed_keys = ", ".join(self.allowed_keys.__dict__.keys())
        raise AttributeError(dedent(f"""\
            Not allowed: '{err_keys}'.
            The only allowed keywords are '{allowed_keys}'.
            """))

    def _valueerror(self, err_values):
        err_values = ", ".join(map(str, err_values))
        allowed_values = ", ".join(map(str, self.allowed_values))
        raise ValueError(dedent(f"""\
            Not allowed: '{err_values}'.
            The only allowed values are '{allowed_values}'.
            """))


# The following names are used literally in this module.
# This way, we avoid the dict hashing problem.
signature = SignatureLayout()

existence = SignatureLayout(definition=False,
                            defaults=False,
                            return_annotation=False,
                            parameter_names=False)

hintingstub = SignatureLayout(ellipsis=True)

typeerror = SignatureLayout(definition=False,
                            return_annotation=False,
                            parameter_names=False)


_POSITIONAL_ONLY         = inspect.Parameter.POSITIONAL_ONLY        # noqa E:201
_POSITIONAL_OR_KEYWORD   = inspect.Parameter.POSITIONAL_OR_KEYWORD  # noqa E:201
_VAR_POSITIONAL          = inspect.Parameter.VAR_POSITIONAL         # noqa E:201
_KEYWORD_ONLY            = inspect.Parameter.KEYWORD_ONLY           # noqa E:201
_VAR_KEYWORD             = inspect.Parameter.VAR_KEYWORD            # noqa E:201
_empty                   = inspect.Parameter.empty                  # noqa E:201

# PYSIDE-3098: Iterable and Sequence can occur together in an overload.
#              This needs sorting in order of generality.
# This happened in the NumPy support of PySide 6.10. Note that the ordering
# of methods there is completely different and unrelated to this mypy sorting.
default_weights = {
    typing.Any: 1000,   # noqa E:241
    Iterable:    401,   # noqa E:241
    Sequence:    400,   # noqa E:241
    bool:        101,   # noqa E:241
    int:         102,   # noqa E:241
    float:       103,   # noqa E:241
    object:      500,   # noqa E:241
}


_ignore_mro = type, None, typing.Any, typing.TypeVar, typing.Type[PlaceholderType]
mro_len = lambda ann: len(ann.mro()) if ann not in _ignore_mro and hasattr(ann, "mro") else 0


def get_ordering_key(anno):
    """
    This is the main sorting algorithm for annotations.
    For a normal type, we use the tuple

        (- length of mro(anno), 1, name)

    For Union expressions, we use the minimum

        (- minlen of mro(anno), len(getargs(anno)), name)

    This way, Union annotations are always sorted behind normal types.
    Addition of a `name` field ensures a unique ordering.

    A special case are numeric types, which have also an ordering between them.
    They can be handled separately, since they are all of the shortest mro.

    PYSIDE-3012: For some reason, we failed to transform `Union[a, b]` directly
                 into `a | b`. Something unknown about comparison must be different.
                 Therefore the transform function was put on top.
    XXX Get rid of the function and document the problem thoroughly.
    """
    typing_type = typing.get_origin(anno)
    is_union = typing_type is typing.Union
    if is_union:
        # This is some Union-like construct.
        typing_args = typing.get_args(anno)
        parts = len(typing_args)

        if defaults := list(ann for ann in typing_args if ann in default_weights):
            # Special: look into the default weights and use the largest.
            leng = 0
            for ann in defaults:
                w = default_weights[ann]
                if w > leng:
                    leng = w
                    anno = ann
        else:
            # Normal: Use the union arg with the shortest mro().
            leng = 9999
            for ann in typing_args:
                lng = mro_len(ann)
                if lng < leng:
                    leng = lng
                    anno = ann
    else:
        leng = mro_len(anno)
        parts = 1
    if anno in default_weights:
        leng = - default_weights[anno]
    # In 3.10 only None has no name. 3.9 is worse concerning typing constructs.
    name = anno.__name__ if hasattr(anno, "__name__") else "None"
    # Put typing containers after the plain type.
    if typing_type:
        return (-leng + 100, parts, name)
    return (-leng, parts, name)


def sort_by_inheritance(signatures):
    # First decorate all signatures with a key built by the mro.
    for idx, sig in enumerate(signatures):
        sort_order = []
        for param in list(sig.parameters.values()):
            sort_order.append(get_ordering_key(param.annotation))
        signatures[idx] = sort_order, sig

    # Sort the signatures and remove the key column again.
    signatures = sorted(signatures, key=lambda x: x[0])
    for idx, sig in enumerate(signatures):
        signatures[idx] = sig[1]
    return signatures


def best_to_remove(signatures, idx1, idx2, name):
    # Both have identical annotation.
    sig1 = signatures[idx1]
    sig2 = signatures[idx2]
    ra1 = sig1.return_annotation
    ra2 = sig2.return_annotation
    # Both have equal return annotations
    if ra1 == ra2:
        for p1, p2 in zip(sig1.parameters.values(), sig2.parameters.values()):
            # Keep the first with a default.
            if p1.default is not _empty or p2.default is not _empty:
                # Note: We return what to remove!
                return idx2 if p1.default is not _empty else idx1
    if ra1 and ra2:
        # Both have a return annotation.
        # Remove the probably uglier of the two. This is likely to be the
        # first one without effort because i.E. arg1 comes early in sorting.
        return idx1
    # Remove the one without a return annotation.
    return idx1 if ra2 is not None else idx2


def _remove_ambiguous_signatures_body(signatures, name):
    # By the sorting of signatures, duplicates will always be adjacent.
    last_ann = None
    last_idx = -1
    to_delete = []
    found = False
    for idx, sig in enumerate(signatures):
        annos = []
        for param in list(sig.parameters.values()):
            annos.append(param.annotation)
        if annos == last_ann:
            found = True
            to_delete.append(best_to_remove(signatures, idx, last_idx, name))
        last_ann = annos
        last_idx = idx

    if not found:
        return False, signatures
    new_sigs = []
    for idx, sig in enumerate(signatures):
        if idx not in to_delete:
            new_sigs.append(sig)
    return True, new_sigs


def remove_ambiguous_signatures(signatures, name):
    # This may run more than once because of indexing.
    found, new_sigs = _remove_ambiguous_signatures_body(signatures, name)
    while found:
        found, new_sigs = _remove_ambiguous_signatures_body(new_sigs, name)
    return new_sigs


def create_signature_union(props, key):
    if not props:
        # empty signatures string
        return
    if isinstance(props["multi"], list):
        # multi sig: call recursively.
        # For debugging: Print the name!
        name = props["multi"][0]["fullname"]
        res = list(create_signature_union(elem, key) for elem in props["multi"])
        # PYSIDE-2846: Sort multi-signatures by inheritance in order to avoid shadowing.
        res = sort_by_inheritance(res)
        res = remove_ambiguous_signatures(res, name)
        return res if len(res) > 1 else res[0]

    if type(key) is tuple:
        _, modifier = key
    else:
        _, modifier = key, "signature"

    layout = globals()[modifier]  # lookup of the modifier in this module
    if not isinstance(layout, SignatureLayout):
        raise SystemError("Modifiers must be names of a SignatureLayout "
                          "instance")

    # this is the basic layout of a signature
    varnames = props["varnames"]
    if not layout.definition:
        if varnames and varnames[0] in ("self", "cls"):
            varnames = varnames[1:]

    # calculate the modifications
    defaults = props["defaults"][:]
    if not layout.defaults:
        defaults = ()
    annotations = props["annotations"].copy()
    if not layout.return_annotation and "return" in annotations:
        del annotations["return"]

    # Build a signature.
    kind = last = DEFAULT_PARAM_KIND
    params = []
    snake_flag = using_snake_case()

    for idx, name in enumerate(varnames):
        if name == "*":
            # This is a switch.
            # Important: It must have a default to simplify the calculation.
            kind = _KEYWORD_ONLY
            continue
        if name.startswith("**"):
            kind = _VAR_KEYWORD
        elif name.startswith("*"):
            kind = _VAR_POSITIONAL
        ann = annotations.get(name, _empty)
        if ann in ("self", "cls"):
            ann = _empty
        name = name.lstrip("*")
        defpos = idx - len(varnames) + len(defaults)
        default = defaults[defpos] if defpos >= 0 else _empty
        if default is not _empty:
            if kind != _KEYWORD_ONLY:
                kind = _POSITIONAL_OR_KEYWORD
                if last == _VAR_POSITIONAL:
                    kind = _KEYWORD_ONLY
        if default is None:
            ann = typing.Union[ann]
            ann = typing.Optional[ann]
        if default is not _empty and layout.ellipsis:
            default = ellipsis
        if kind is _KEYWORD_ONLY:
            # All these entries are properties. They might have been used already
            # as normal parameter before and must be omitted here. Fixing that now:
            if varnames.count(name) > 1:
                assert varnames.count(name) == 2
                if snake_flag and name != (new_name := make_snake_case_name(name)):
                    # Patch this name backwards because it comes earlier as property.
                    idx = varnames.index(name)
                    params[idx] = params[idx].replace(name=new_name)
                continue
            if snake_flag:
                name = make_snake_case_name(name)
        last = kind
        param = inspect.Parameter(name, kind, annotation=ann, default=default)
        params.append(param)

    # Find the index of variadic positional parameter, if any
    # And update the parameter kind that comes after
    idx = next((i for i, p in enumerate(params) if p.kind == _VAR_POSITIONAL), None)
    if idx is not None:
        for i, p in enumerate(params):
            if i > idx and p.kind != _VAR_KEYWORD:
                params[i] = p.replace(kind=_KEYWORD_ONLY)

    ret_anno = annotations.get('return', _empty)
    if ret_anno is not _empty and props["fullname"] in missing_optional_return:
        ret_anno = typing.Union[ret_anno]
        ret_anno = typing.Optional[ret_anno]
    return inspect.Signature(params, return_annotation=ret_anno,
                             __validate_parameters__=False)


def transform(signature):
    # Change the annotations of the parameters to use "|" syntax.
    params = []
    changed = False
    for idx, param in enumerate(signature.parameters.values()):
        ann = param.annotation
        if typing.get_origin(ann) is typing.Union:
            args = typing.get_args(ann)
            ann = reduce(operator.or_, args)
            param = param.replace(annotation=ann)
            changed = True
        params.append(param)
    ann = signature.return_annotation
    if typing.get_origin(ann) is typing.Union:
        args = typing.get_args(ann)
        ann = reduce(operator.or_, args)
        changed = True
    return signature.replace(parameters=params, return_annotation=ann) if changed else signature


def create_signature(props, key):
    res = create_signature_union(props, key)
    if type(res) is list:
        for idx, sig in enumerate(res):
            res[idx] = transform(sig)
    else:
        res = transform(res)
    return res

# end of file
