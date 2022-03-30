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
