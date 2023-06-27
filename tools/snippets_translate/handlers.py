# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import re
import sys

from parse_utils import (dstrip, get_indent, get_qt_module_class,
                         parse_arguments, remove_ref, replace_main_commas)

IF_PATTERN = re.compile(r'^\s*if\s*\(')
PARENTHESES_NONEMPTY_CONTENT_PATTERN = re.compile(r"\((.+)\)")
LOCAL_INCLUDE_PATTERN = re.compile(r'"(.*)"')
GLOBAL_INCLUDE_PATTERN = re.compile(r"<(.*)>")
IF_CONDITION_PATTERN = PARENTHESES_NONEMPTY_CONTENT_PATTERN
ELSE_IF_PATTERN = re.compile(r'^\s*}?\s*else if\s*\(')
WHILE_PATTERN = re.compile(r'^\s*while\s*\(')
CAST_PATTERN = re.compile(r"[a-z]+_cast<(.*?)>\((.*?)\)")  # Non greedy match of <>
ITERATOR_LOOP_PATTERN = re.compile(r"= *(.*)egin\(")
REMOVE_TEMPLATE_PARAMETER_PATTERN = re.compile("<.*>")
PARENTHESES_CONTENT_PATTERN = re.compile(r"\((.*)\)")
CONSTRUCTOR_BODY_PATTERN = re.compile(".*{ *}.*")
CONSTRUCTOR_BODY_REPLACEMENT_PATTERN = re.compile("{ *}")
CONSTRUCTOR_BASE_PATTERN = re.compile("^ *: *")
NEGATE_PATTERN = re.compile(r"!(.)")
CLASS_TEMPLATE_PATTERN = re.compile(r".*<.*>")
EMPTY_CLASS_PATTERN = re.compile(r".*{.*}")
EMPTY_CLASS_REPLACEMENT_PATTERN = re.compile(r"{.*}")
FUNCTION_BODY_PATTERN = re.compile(r"\{(.*)\}")
ARRAY_DECLARATION_PATTERN = re.compile(r"^[a-zA-Z0-9\<\>]+ ([\w\*]+) *\[?\]?")
RETURN_TYPE_PATTERN = re.compile(r"^ *[a-zA-Z0-9]+ [\w]+::([\w\*\&]+\(.*\)$)")
CAPTURE_PATTERN = re.compile(r"^ *([a-zA-Z0-9]+) ([\w\*\&]+\(.*\)$)")
USELESS_QT_CLASSES_PATTERNS = [
    re.compile(r'QLatin1StringView\(("[^"]*")\)'),
    re.compile(r'QLatin1String\(("[^"]*")\)'),
    re.compile(r'QString\.fromLatin1\(("[^"]*")\)'),
    re.compile(r"QLatin1Char\(('[^']*')\)"),
    re.compile(r'QStringLiteral\(("[^"]*")\)'),
    re.compile(r'QString\.fromUtf8\(("[^"]*")\)'),
    re.compile(r'u("[^"]*")_s')
]
COMMENT1_PATTERN = re.compile(r" *# *[\w\ ]+$")
COMMENT2_PATTERN = re.compile(r" *# *(.*)$")
COUT_ENDL_PATTERN = re.compile(r"cout *<<(.*)<< *.*endl")
COUT1_PATTERN = re.compile(r" *<< *")
COUT2_PATTERN = re.compile(r".*cout *<<")
COUT_ENDL2_PATTERN = re.compile(r"<< +endl")
NEW_PATTERN = re.compile(r"new +([a-zA-Z][a-zA-Z0-9_]*)")


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

        match = IF_CONDITION_PATTERN.search(x)
        if match:
            condition = match.group(1)
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
    while True:
        match = CAST_PATTERN.search(x)
        if not match:
            break
        type_name = match.group(1).strip()
        while type_name.endswith("*") or type_name.endswith("&") or type_name.endswith(" "):
            type_name = type_name[:-1]
        data_name = match.group(2).strip()
        python_cast = f"{type_name}({data_name})"
        x = x[0:match.start(0)] + python_cast + x[match.end(0):]

    return x


def handle_include(x):
    if '"' in x:
        header = LOCAL_INCLUDE_PATTERN.search(x)
        if header:
            header_name = header.group(1).replace(".h", "")
            module_name = header_name.replace('/', '.')
            x = f"from {module_name} import *"
        else:
            # We discard completely if there is something else
            # besides '"something.h"'
            x = ""
    elif "<" in x and ">" in x:
        name = GLOBAL_INCLUDE_PATTERN.search(x).group(1)
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
    content = PARENTHESES_CONTENT_PATTERN.search(x)

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
                name = ITERATOR_LOOP_PATTERN.search(start)
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
                    if not start.strip() or "=" not in start:
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
            iterable = iterable.strip()
            if iterable.startswith("qAsConst(") or iterable.startswith("std::as_const("):
                iterable = iterable[iterable.find("(") + 1: -1]
            new_x = f"for {remove_ref(var)} in {iterable}:"
    return f"{get_indent(x)}{dstrip(new_x)}"


def handle_foreach(x):
    content = PARENTHESES_CONTENT_PATTERN.search(x)
    if content:
        parenthesis = content.group(1)
        iterator, iterable = parenthesis.split(",", 1)
        # remove iterator type
        it = dstrip(iterator.split()[-1])
        # remove <...> from iterable
        value = REMOVE_TEMPLATE_PARAMETER_PATTERN.sub("", iterable)
        return f"{get_indent(x)}for {it} in {value}:"


def handle_type_var_declaration(x):
    # remove content between <...>
    if "<" in x and ">" in x:
        x = " ".join(REMOVE_TEMPLATE_PARAMETER_PATTERN.sub("", i) for i in x.split())
    content = PARENTHESES_CONTENT_PATTERN.search(x)
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
    arguments = PARENTHESES_CONTENT_PATTERN.search(x).group(1)
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
    if CONSTRUCTOR_BODY_PATTERN.search(x):
        x = CONSTRUCTOR_BODY_REPLACEMENT_PATTERN.sub("", x)

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
            arg = CONSTRUCTOR_BASE_PATTERN.sub("", arg).strip()
            if arg.startswith("Q"):
                class_name = arg.split("(")[0]
                content = arg.replace(class_name, "")[1:-1]
                return_values += f"    super().__init__({content})\n"
            elif arg:
                var_name = arg.split("(")[0]
                content = PARENTHESES_NONEMPTY_CONTENT_PATTERN.search(arg).group(1)
                return_values += f"    self.{var_name} = {content}\n"
    else:
        arg = CONSTRUCTOR_BASE_PATTERN.sub("", values).strip()
        if arg.startswith("Q"):
            class_name = arg.split("(")[0]
            content = arg.replace(class_name, "")[1:-1]
            return f"    super().__init__({content})"
        elif arg:
            var_name = arg.split("(")[0]
            match = PARENTHESES_NONEMPTY_CONTENT_PATTERN.search(arg)
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
    if COMMENT1_PATTERN.search(x):
        match = COMMENT2_PATTERN.search(x).group(1)
        comment = f' # {match}'
        x = x.split("#")[0]

    if "qDebug()" in x:
        x = x.replace("qDebug()", "cout")

    if "cout" in x and "endl" in x:
        data = COUT_ENDL_PATTERN.search(x)
        if data:
            data = data.group(1)
            data = COUT1_PATTERN.sub(", ", data)
            x = f"{get_indent(x)}print({data}){comment}"
    elif "cout" in x:
        data = COUT2_PATTERN.sub("", x)
        data = COUT1_PATTERN.sub(", ", data)
        x = f"{get_indent(x)}print({data}){comment}"
    elif "endl" in x:
        data = COUT_ENDL2_PATTERN.sub("", x)
        data = COUT1_PATTERN.sub(", ", data)
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
    next_char = NEGATE_PATTERN.search(x).group(1)
    if next_char not in ("=", '"'):
        x = x.replace("!", "not ")
    return x


def handle_emit(x):
    function_call = x.replace("emit ", "").strip()
    match = PARENTHESES_CONTENT_PATTERN.search(function_call)
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
        parenthesis = PARENTHESES_CONTENT_PATTERN.search(x).group(1)
        arguments = dstrip(parse_arguments(parenthesis))
    elif "," in x:
        arguments = dstrip(parse_arguments(x.split("(")[-1]))

    # check if includes a '{ ... }' after the method signature
    after_signature = x.split(")")[-1]
    re_decl = FUNCTION_BODY_PATTERN.search(after_signature)
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
    if CLASS_TEMPLATE_PATTERN.search(class_name):
        class_name = class_name.split("<")[0]

    # Special case: invalid notation for an example:
    #   class B() {...} -> clas B(): pass
    if EMPTY_CLASS_PATTERN.search(class_name):
        class_name = EMPTY_CLASS_REPLACEMENT_PATTERN.sub("", class_name).rstrip()
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
    content = ARRAY_DECLARATION_PATTERN.search(x.strip())
    if content:
        var_name = content.group(1)
        rest_line = "".join(x.split("{")[1:])
        x = f"{get_indent(x)}{var_name} = {{{rest_line}"
    return x


def handle_methods_return_type(x):
    capture = RETURN_TYPE_PATTERN.search(x)
    if capture:
        content = capture.group(1)
        method_name = content.split("(")[0]
        par_capture = PARENTHESES_NONEMPTY_CONTENT_PATTERN.search(x)
        arguments = "(self)"
        if par_capture:
            arguments = f"(self, {par_capture.group(1)})"
        x = f"{get_indent(x)}def {method_name}{arguments}:"
    return x


def handle_functions(x):
    capture = CAPTURE_PATTERN.search(x)
    if capture:
        return_type = capture.group(1)
        if return_type == "return":  # "return QModelIndex();"
            return x
        content = capture.group(2)
        function_name = content.split("(")[0]
        par_capture = PARENTHESES_NONEMPTY_CONTENT_PATTERN.search(x)
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
    for c in USELESS_QT_CLASSES_PATTERNS:
        while True:
            match = c.search(x)
            if match:
                x = x[0:match.start()] + match.group(1) + x[match.end():]
            else:
                break
    return x.replace('"_L1', '"').replace("u'", "'")


def handle_new(x):
    """Parse operator new() and add parentheses were needed:
       func(new Foo, new Bar(x))" -> "func(Foo(), Bar(x))"""
    result = ""
    last_pos = 0
    for match in NEW_PATTERN.finditer(x):
        end = match.end(0)
        parentheses_needed = end >= len(x) or x[end] != "("
        type_name = match.group(1)
        result += x[last_pos:match.start(0)] + type_name
        if parentheses_needed:
            result += "()"
        last_pos = end
    result += x[last_pos:]
    return result


# The code below handles pairs of instance/pointer to member functions (PMF)
# which appear in Qt in connect statements like:
# "connect(fontButton, &QAbstractButton::clicked, this, &Dialog::setFont)".
# In a first pass, these pairs are replaced by:
# "connect(fontButton.clicked, self.setFont)" to be able to handle statements
# spanning lines. A 2nd pass then checks for the presence of a connect
# statement and replaces it by:
# "fontButton.clicked.connect(self.setFont)".
# To be called right after checking for comments.


INSTANCE_PMF_RE = re.compile(r"&?(\w+),\s*&\w+::(\w+)")


CONNECT_RE = re.compile(r"^(\s*)(QObject::)?connect\(([A-Za-z0-9_\.]+),\s*")


def handle_qt_connects(line_in):
    if not INSTANCE_PMF_RE.search(line_in):
        return None
    # 1st pass, "fontButton, &QAbstractButton::clicked" -> "fontButton.clicked"

    is_connect = "connect(" in line_in
    line = line_in
    # Remove any smart pointer access, etc in connect statements
    if is_connect:
        line = line.replace(".get()", "").replace(".data()", "").replace("->", ".")
    last_pos = 0
    result = ""
    for match in INSTANCE_PMF_RE.finditer(line):
        instance = match.group(1)
        if instance == "this":
            instance = "self"
        member_fun = match.group(2)
        next_pos = match.start()
        result += line[last_pos:next_pos]
        last_pos = match.end()
        result += f"{instance}.{member_fun}"
    result += line[last_pos:]

    if not is_connect:
        return result

    # 2nd pass, reorder connect.
    connect_match = CONNECT_RE.match(result)
    if not connect_match:
        return result

    space = connect_match.group(1)
    signal_ = connect_match.group(3)
    connect_stmt = f"{space}{signal_}.connect("
    connect_stmt += result[connect_match.end():]
    return connect_stmt
