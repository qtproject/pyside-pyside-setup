# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import re

from module_classes import module_classes


def get_qt_module_class(x):
    """
    Receives the name of an include:
        'QSomething' from '#include <QSomething>'

    Returns a tuple '(bool, str)' where the 'bool' is True if the name is
    a module by itself, like QtCore or QtWidgets, and False if it's a class
    from one of those modules. The 'str' returns the name of the module
    where the class belongs, or the same module.

    In case it doesn't find the class or the module, it will return None.
    """
    if "/" in x:
        x = x.split("/")[-1]

    for imodule, iclasses in module_classes.items():
        if imodule == x:
            return True, x
        for iclass in iclasses:
            if iclass == x:
                return False, imodule
    return None


def get_indent(x):
    return " " * (len(x) - len(x.lstrip()))


# Remove more than one whitespace from the code, but not considering
# the indentation. Also removes '&', '*', and ';' from arguments.
def dstrip(x):
    right = x
    if re.search(r"\s+", x):
        right = re.sub(" +", " ", x).strip()
    if "&" in right:
        right = right.replace("&", "")

    if "*" in right:
        re_pointer = re.compile(r"\*(.)")
        next_char = re_pointer.search(x)
        if next_char:
            if next_char.group(1).isalpha():
                right = right.replace("*", "")

    if right.endswith(";"):
        right = right.replace(";", "")
    x = f"{get_indent(x)}{right}"

    return x


def remove_ref(var_name):
    var = var_name.strip()
    while var.startswith("*") or var.startswith("&"):
        var = var[1:]
    return var.lstrip()


def parse_arguments(p):
    unnamed_var = 0
    if "," in p:
        v = ""
        for i, arg in enumerate(p.split(",")):
            if i != 0:
                v += ", "
            if arg:
                new_value = arg.split()[-1]
                # handle no variable name
                if new_value.strip() == "*":
                    v += f"arg__{unnamed_var}"
                    unnamed_var += 1
                else:
                    v += arg.split()[-1]
    elif p.strip():
        new_value = p.split()[-1]
        if new_value.strip() == "*":
            v = f"arg__{unnamed_var}"
        else:
            v = new_value
    else:
        v = p

    return v


def replace_main_commas(v):
    #   : QWidget(parent), Something(else, and, other), value(1)
    new_v = ""
    parenthesis = 0
    for c in v:
        if c == "(":
            parenthesis += 1
        elif c == ")":
            parenthesis -= 1

        if c == "," and parenthesis == 0:
            c = "@"

        new_v += c

    return new_v
