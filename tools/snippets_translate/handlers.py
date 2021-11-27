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
import sys

from parse_utils import get_indent, dstrip, remove_ref, parse_arguments, replace_main_commas, get_qt_module_class

IF_PATTERN = re.compile(r'^if\s*\(')
ELSE_IF_PATTERN = re.compile(r'^}?\s*else if\s*\(')
WHILE_PATTERN = re.compile(r'^while\s*\(')


def handle_condition(x, name):
    # Make sure it's not a multi line condition
    x = x.replace("}", "")
    if x.count("(") == x.count(")"):
        comment = ""
        # This handles the lines that have no ';' at the end but
        # have a comment after the end of the line, like:
        #   while (true) // something
        #   { ... }
        if "//" in x:
            comment_content = x.split("//", 1)
            comment = f"  #{comment_content[-1]}"
            x = x.replace(f"//{comment_content[-1]}", "")

        re_par = re.compile(r"\((.+)\)")
        match = re_par.search(x)
        if match:
            condition = re_par.search(x).group(1)
            return f"{get_indent(x)}{name} {condition.strip()}:{comment}"
        else:
            print(f'snippets_translate: Warning "{x}" does not match condition pattern',
                  file=sys.stderr)
    return x


def handle_keywords(x, word, pyword):
    if word in x:
        if "#" in x:
            if x.index(word) < x.index("#"):
                x = x.replace(word, pyword)
        else:
            x = x.replace(word, pyword)
    return x


def handle_inc_dec(x, operator):
    # Alone on a line
    clean_x = x.strip()
    if clean_x.startswith(operator) or clean_x.endswith(operator):
        x = x.replace(operator, "")
        x = f"{x} = {clean_x.replace(operator, '')} {operator[0]} 1"
    return x


def handle_casts(x):
    cast = None
    re_type = re.compile(r"<(.*)>")
    re_data = re.compile(r"_cast<.*>\((.*)\)")
    type_name = re_type.search(x)
    data_name = re_data.search(x)

    if type_name and data_name:
        type_name = type_name.group(1).replace("*", "")
        data_name = data_name.group(1)
        new_value = f"{type_name}({data_name})"

        if "static_cast" in x:
            x = re.sub(r"static_cast<.*>\(.*\)", new_value, x)
        elif "dynamic_cast" in x:
            x = re.sub(r"dynamic_cast<.*>\(.*\)", new_value, x)
        elif "const_cast" in x:
            x = re.sub(r"const_cast<.*>\(.*\)", new_value, x)
        elif "reinterpret_cast" in x:
            x = re.sub(r"reinterpret_cast<.*>\(.*\)", new_value, x)
        elif "qobject_cast" in x:
            x = re.sub(r"qobject_cast<.*>\(.*\)", new_value, x)

    return x


def handle_include(x):
    if '"' in x:
        re_par = re.compile(r'"(.*)"')
        header = re_par.search(x)
        if header:
            header_name = header.group(1).replace(".h", "")
            module_name = header_name.replace('/', '.')
            x = f"from {module_name} import *"
        else:
            # We discard completely if there is something else
            # besides '"something.h"'
            x = ""
    elif "<" in x and ">" in x:
        re_par = re.compile(r"<(.*)>")
        name = re_par.search(x).group(1)
        t = get_qt_module_class(name)
        # if it's not a Qt module or class, we discard it.
        if t is None:
            x = ""
        else:
            # is a module
            if t[0]:
                x = f"from PySide6 import {t[1]}"
            # is a class
            else:
                x = f"from PySide6.{t[1]} import {name}"
    return x


def handle_conditions(x):
    x_strip = x.strip()
    if WHILE_PATTERN.match(x):
        x = handle_condition(x, "while")
    elif IF_PATTERN.match(x):
        x = handle_condition(x, "if")
    elif ELSE_IF_PATTERN.match(x):
        x = handle_condition(x, "else if")
        x = x.replace("else if", "elif")
    x = x.replace("::", ".")
    return x


def handle_for(x):
    re_content = re.compile(r"\((.*)\)")
    content = re_content.search(x)

    new_x = x
    if content:
        # parenthesis content
        content = content.group(1)

        # for (int i = 1; i < argc; ++i)
        if x.count(";") == 2:

            # for (start; middle; end)
            start, middle, end = content.split(";")

            # iterators
            if "begin(" in x.lower() and "end(" in x.lower():
                name = re.search(r"= *(.*)egin\(", start)
                iterable = None
                iterator = None
                if name:
                    name = name.group(1)
                    # remove initial '=', and split the '.'
                    # because '->' was already transformed,
                    # and we keep the first word.
                    iterable = name.replace("=", "", 1).split(".")[0]

                iterator = remove_ref(start.split("=")[0].split()[-1])
                if iterator and iterable:
                    return f"{get_indent(x)}for {iterator} in {iterable}:"

            if ("++" in end or "--" in end) or ("+=" in end or "-=" in end):
                if "," in start:
                    raw_var, value = start.split(",")[0].split("=")
                else:
                    # Malformed for-loop:
                    #   for (; pixel1 > start; pixel1 -= stride)
                    # We return the same line
                    if not start.strip() or not "=" in start:
                        return f"{get_indent(x)}{dstrip(x)}"
                    raw_var, value = start.split("=")
                raw_var = raw_var.strip()
                value = value.strip()
                var = raw_var.split()[-1]

                end_value = None
                if "+=" in end:
                    end_value = end.split("+=")[-1]
                elif "-=" in end:
                    end_value = end.split("-=")[-1]
                if end_value:
                    try:
                        end_value = int(end_value)
                    except ValueError:
                        end_value = None

                if "<" in middle:
                    limit = middle.split("<")[-1]

                    if "<=" in middle:
                        limit = middle.split("<=")[-1]
                        try:
                            limit = int(limit)
                            limit += 1
                        except ValueError:
                            limit = f"{limit} + 1"

                    if end_value:
                        new_x = f"for {var} in range({value}, {limit}, {end_value}):"
                    else:
                        new_x = f"for {var} in range({value}, {limit}):"
                elif ">" in middle:
                    limit = middle.split(">")[-1]

                    if ">=" in middle:
                        limit = middle.split(">=")[-1]
                        try:
                            limit = int(limit)
                            limit -= 1
                        except ValueError:
                            limit = f"{limit} - 1"
                    if end_value:
                        new_x = f"for {var} in range({limit}, {value}, -{end_value}):"
                    else:
                        new_x = f"for {var} in range({limit}, {value}, -1):"
                else:
                    # TODO: No support if '<' or '>' is not used.
                    pass

        # for (const QByteArray &ext : qAsConst(extensionList))
        elif x.count(":") > 0:
            iterator, iterable = content.split(":", 1)
            var = iterator.split()[-1].replace("&", "").strip()
            new_x = f"for {remove_ref(var)} in {iterable.strip()}:"
    return f"{get_indent(x)}{dstrip(new_x)}"


def handle_foreach(x):
    re_content = re.compile(r"\((.*)\)")
    content = re_content.search(x)
    if content:
        parenthesis = content.group(1)
        iterator, iterable = parenthesis.split(",", 1)
        # remove iterator type
        it = dstrip(iterator.split()[-1])
        # remove <...> from iterable
        value = re.sub("<.*>", "", iterable)
        return f"{get_indent(x)}for {it} in {value}:"


def handle_type_var_declaration(x):
    # remove content between <...>
    if "<" in x and ">" in x:
        x = " ".join(re.sub("<.*>", "", i) for i in x.split())
    content = re.search(r"\((.*)\)", x)
    if content:
        # this means we have something like:
        #   QSome thing(...)
        type_name, var_name = x.split()[:2]
        var_name = var_name.split("(")[0]
        x = f"{get_indent(x)}{var_name} = {type_name}({content.group(1)})"
    else:
        # this means we have something like:
        #   QSome thing
        type_name, var_name = x.split()[:2]
        x = f"{get_indent(x)}{var_name} = {type_name}()"
    return x


def handle_constructors(x):
    re_content = re.compile(r"\((.*)\)")
    arguments = re_content.search(x).group(1)
    class_method = x.split("(")[0].split("::")
    if len(class_method) == 2:
        # Equal 'class name' and 'method name'
        if len(set(class_method)) == 1:
            arguments = ", ".join(remove_ref(i.split()[-1]) for i in arguments.split(",") if i)
            if arguments:
                return f"{get_indent(x)}def __init__(self, {arguments}):"
            else:
                return f"{get_indent(x)}def __init__(self):"
    return dstrip(x)


def handle_constructor_default_values(x):
    # if somehow we have a ' { } ' by the end of the line,
    # we discard that section completely, since even with a single
    # value, we don't need to take care of it, for example:
    # ' : a(1) { }     ->   self.a = 1
    if re.search(".*{ *}.*", x):
        x = re.sub("{ *}", "", x)

    values = "".join(x.split(":", 1))
    # Check the commas that are not inside round parenthesis
    # For example:
    #   : QWidget(parent), Something(else, and, other), value(1)
    # so we can find only the one after '(parent),' and 'other),'
    # and replace them by '@'
    #   : QWidget(parent)@ Something(else, and, other)@ value(1)
    # to be able to split the line.
    values = replace_main_commas(values)
    # if we have more than one expression
    if "@" in values:
        return_values = ""
        for arg in values.split("@"):
            arg = re.sub("^ *: *", "", arg).strip()
            if arg.startswith("Q"):
                class_name = arg.split("(")[0]
                content = arg.replace(class_name, "")[1:-1]
                return_values += f"    {class_name}.__init__(self, {content})\n"
            elif arg:
                var_name = arg.split("(")[0]
                re_par = re.compile(r"\((.+)\)")
                content = re_par.search(arg).group(1)
                return_values += f"    self.{var_name} = {content}\n"
    else:
        arg = re.sub("^ *: *", "", values).strip()
        if arg.startswith("Q"):
            class_name = arg.split("(")[0]
            content = arg.replace(class_name, "")[1:-1]
            return f"    {class_name}.__init__(self, {content})"
        elif arg:
            var_name = arg.split("(")[0]
            re_par = re.compile(r"\((.+)\)")
            match = re_par.search(arg)
            if match:
                content = match.group(1)
                return f"    self.{var_name} = {content}"
            else:
                print(f'snippets_translate: Warning "{arg}" does not match pattern',
                      file=sys.stderr)
                return ""
    return return_values.rstrip()


def handle_cout_endl(x):
    # if comment at the end
    comment = ""
    if re.search(r" *# *[\w\ ]+$", x):
        comment = f' # {re.search(" *# *(.*)$", x).group(1)}'
        x = x.split("#")[0]

    if "qDebug()" in x:
        x = x.replace("qDebug()", "cout")

    if "cout" in x and "endl" in x:
        re_cout_endl = re.compile(r"cout *<<(.*)<< *.*endl")
        data = re_cout_endl.search(x)
        if data:
            data = data.group(1)
            data = re.sub(" *<< *", ", ", data)
            x = f"{get_indent(x)}print({data}){comment}"
    elif "cout" in x:
        data = re.sub(".*cout *<<", "", x)
        data = re.sub(" *<< *", ", ", data)
        x = f"{get_indent(x)}print({data}){comment}"
    elif "endl" in x:
        data = re.sub("<< +endl", "", x)
        data = re.sub(" *<< *", ", ", data)
        x = f"{get_indent(x)}print({data}){comment}"

    x = x.replace("( ", "(").replace(" )", ")").replace(" ,", ",").replace("(, ", "(")
    x = x.replace("Qt.endl", "").replace(", )", ")")
    return x


def handle_negate(x):
    # Skip if it's part of a comment:
    if "#" in x:
        if x.index("#") < x.index("!"):
            return x
    elif "/*" in x:
        if x.index("/*") < x.index("!"):
            return x
    re_negate = re.compile(r"!(.)")
    next_char = re_negate.search(x).group(1)
    if next_char not in ("=", '"'):
        x = x.replace("!", "not ")
    return x


def handle_emit(x):
    function_call = x.replace("emit ", "").strip()
    re_content = re.compile(r"\((.*)\)")
    match = re_content.search(function_call)
    if not match:
        stmt = x.strip()
        print(f'snippets_translate: Warning "{stmt}" does not match function call',
              file=sys.stderr)
        return ''
    arguments = match.group(1)
    method_name = function_call.split("(")[0].strip()
    return f"{get_indent(x)}{method_name}.emit({arguments})"


def handle_void_functions(x):
    class_method = x.replace("void ", "").split("(")[0]
    first_param = ""
    if "::" in class_method:
        first_param = "self, "
        method_name = class_method.split("::")[1]
    else:
        method_name = class_method.strip()

    # if the arguments are in the same line:
    arguments = None
    if ")" in x:
        re_content = re.compile(r"\((.*)\)")
        parenthesis = re_content.search(x).group(1)
        arguments = dstrip(parse_arguments(parenthesis))
    elif "," in x:
        arguments = dstrip(parse_arguments(x.split("(")[-1]))

    # check if includes a '{ ... }' after the method signature
    after_signature = x.split(")")[-1]
    re_decl = re.compile(r"\{(.*)\}").search(after_signature)
    extra = ""
    if re_decl:
        extra = re_decl.group(1)
        if not extra:
            extra = " pass"

    if arguments:
        x = f"{get_indent(x)}def {method_name}({first_param}{dstrip(arguments)}):{extra}"
    else:
        x = f"{get_indent(x)}def {method_name}({first_param.replace(', ', '')}):{extra}"
    return x


def handle_class(x):
    # Check if there is a comment at the end of the line
    comment = ""
    if "//" in x:
        parts = x.split("//")
        x = "".join(parts[:-1])
        comment = parts[-1]

    # If the line ends with '{'
    if x.rstrip().endswith("{"):
        x = x[:-1]

    # Get inheritance
    decl_parts = x.split(":")
    class_name = decl_parts[0].rstrip()
    if len(decl_parts) > 1:
        bases = decl_parts[1]
        bases_name = ", ".join(i.split()[-1] for i in bases.split(",") if i)
    else:
        bases_name = ""

    # Check if the class_name is templated, then remove it
    if re.search(r".*<.*>", class_name):
        class_name = class_name.split("<")[0]

    # Special case: invalid notation for an example:
    #   class B() {...} -> clas B(): pass
    if re.search(r".*{.*}", class_name):
        class_name = re.sub(r"{.*}", "", class_name).rstrip()
        return f"{class_name}(): pass"

    # Special case: check if the line ends in ','
    if x.endswith(","):
        x = f"{class_name}({bases_name},"
    else:
        x = f"{class_name}({bases_name}):"

    if comment:
        return f"{x} #{comment}"
    else:
        return x

def handle_array_declarations(x):
    re_varname = re.compile(r"^[a-zA-Z0-9\<\>]+ ([\w\*]+) *\[?\]?")
    content = re_varname.search(x.strip())
    if content:
        var_name = content.group(1)
        rest_line = "".join(x.split("{")[1:])
        x = f"{get_indent(x)}{var_name} = {{{rest_line}"
    return x

def handle_methods_return_type(x):
    re_capture = re.compile(r"^ *[a-zA-Z0-9]+ [\w]+::([\w\*\&]+\(.*\)$)")
    capture = re_capture.search(x)
    if capture:
        content = capture.group(1)
        method_name = content.split("(")[0]
        re_par = re.compile(r"\((.+)\)")
        par_capture = re_par.search(x)
        arguments = "(self)"
        if par_capture:
            arguments = f"(self, {par_capture.group(1)})"
        x = f"{get_indent(x)}def {method_name}{arguments}:"
    return x


def handle_functions(x):
    re_capture = re.compile(r"^ *[a-zA-Z0-9]+ ([\w\*\&]+\(.*\)$)")
    capture = re_capture.search(x)
    if capture:
        content = capture.group(1)
        function_name = content.split("(")[0]
        re_par = re.compile(r"\((.+)\)")
        par_capture = re_par.search(x)
        arguments = ""
        if par_capture:
            for arg in par_capture.group(1).split(","):
                arguments += f"{arg.split()[-1]},"
            # remove last comma
            if arguments.endswith(","):
                arguments = arguments[:-1]
        x = f"{get_indent(x)}def {function_name}({dstrip(arguments)}):"
    return x

def handle_useless_qt_classes(x):
    _classes = ("QLatin1String", "QLatin1Char")
    for i in _classes:
        re_content = re.compile(fr"{i}\((.*)\)")
        content = re_content.search(x)
        if content:
            x = x.replace(content.group(0), content.group(1))
    return x
