# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import re

from handlers import (handle_array_declarations, handle_casts, handle_class,
                      handle_conditions, handle_constructor_default_values,
                      handle_constructors, handle_cout_endl, handle_emit,
                      handle_for, handle_foreach, handle_functions,
                      handle_inc_dec, handle_include, handle_keywords,
                      handle_methods_return_type, handle_negate,
                      handle_type_var_declaration, handle_useless_qt_classes,
                      handle_new,
                      handle_void_functions, handle_qt_connects)
from parse_utils import dstrip, get_indent, remove_ref


VOID_METHOD_PATTERN = re.compile(r"^ *void *[\w\_]+(::)?[\w\d\_]+\(")
QT_QUALIFIER_PATTERN = re.compile(r"Q[\w]+::")
TERNARY_OPERATOR_PATTERN = re.compile(r"^.* \? .+ : .+$")
COUT_PATTERN = re.compile("^ *(std::)?cout")
FOR_PATTERN = re.compile(r"^ *for *\(")
FOREACH_PATTERN = re.compile(r"^ *foreach *\(")
ELSE_PATTERN = re.compile(r"^ *}? *else *{?")
ELSE_REPLACEMENT_PATTERN = re.compile(r"}? *else *{?")
CLASS_PATTERN = re.compile(r"^ *class ")
STRUCT_PATTERN = re.compile(r"^ *struct ")
DELETE_PATTERN = re.compile(r"^ *delete ")
VAR1_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*\&]+(\(.*?\))? ?(?!.*=|:).*$")
VAR2_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w]+::[\w\*\&]+\(.*\)$")
VAR3_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+ *= *[\w\.\"\']*(\(.*?\))?")
VAR4_PATTERN = re.compile(r"\w+ = [A-Z]{1}\w+")
CONSTRUCTOR_PATTERN = re.compile(r"^ *\w+::\w+\(.*?\)")
ARRAY_VAR_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+\[?\]? * =? *\{")
RETURN_TYPE_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w]+::[\w\*\&]+\(.*\)$")
FUNCTION_PATTERN = re.compile(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*\&]+\(.*\)$")
ITERATOR_PATTERN = re.compile(r"(std::)?[\w]+<[\w]+>::(const_)?iterator")
SCOPE_PATTERN = re.compile(r"[\w]+::")
SWITCH_PATTERN = re.compile(r"^\s*switch\s*\(([a-zA-Z0-9_\.]+)\)\s*{.*$")
CASE_PATTERN = re.compile(r"^(\s*)case\s+([a-zA-Z0-9_:\.]+):.*$")
DEFAULT_PATTERN = re.compile(r"^(\s*)default:.*$")


QUALIFIERS = {"public:", "protected:", "private:", "public slots:",
              "protected slots:", "private slots:", "signals:"}


FUNCTION_QUALIFIERS = ["virtual ", " override", "inline ", " noexcept"]


switch_var = None
switch_branch = 0


def snippet_translate(x):
    global switch_var, switch_branch

    ## Cases which are not C++
    ## TODO: Maybe expand this with lines that doesn't need to be translated
    if x.strip().startswith("content-type: text/html"):
        return x

    ## General Rules

    # Remove ';' at the end of the lines
    has_semicolon = x.endswith(";")
    if has_semicolon:
        x = x[:-1]

    # Remove lines with only '{' or '}'
    xs = x.strip()
    if xs == "{" or xs == "}":
        return ""

    # Skip lines with the snippet related identifier '//!'
    if xs.startswith("//!"):
        return x

    # handle lines with only comments using '//'
    if xs.startswith("//"):
        x = x.replace("//", "#", 1)
        return x

    qt_connects = handle_qt_connects(x)
    if qt_connects:
        return qt_connects

    # Handle "->"
    if "->" in x:
        x = x.replace("->", ".")

    # handle '&&' and '||'
    if "&&" in x:
        x = x.replace("&&", "and")
    if "||" in x:
        x = x.replace("||", "or")

    # Handle lines that have comments after the ';'
    if ";" in x and "//" in x:
        if x.index(";") < x.index("//"):
            left, right = x.split("//", 1)
            left = left.replace(";", "", 1)
            x = f"{left}#{right}"

    # Handle 'new '
    # This contains an extra whitespace because of some variables
    # that include the string 'new'
    if "new " in x:
        x = handle_new(x)

    # Handle 'const'
    # Some variables/functions have the word 'const' so we explicitly
    # consider the cases with a whitespace before and after.
    if " const" in x:
        x = x.replace(" const", "")
    if "const " in x:
        x = x.replace("const ", "")

    # Handle 'static'
    if "static " in x:
        x = x.replace("static ", "")

    # Handle 'inline'
    if "inline " in x:
        x = x.replace("inline ", "")

    # Handle 'double'
    if "double " in x:
        x = x.replace("double ", "float ")

    # Handle increment/decrement operators
    if "++" in x:
        x = handle_inc_dec(x, "++")
    if "--" in x:
        x = handle_inc_dec(x, "--")

    # handle negate '!'
    if "!" in x:
        x = handle_negate(x)

    # Handle "this", "true", "false" but before "#" symbols
    if "this" in x:
        x = handle_keywords(x, "this", "self")
    if "true" in x:
        x = handle_keywords(x, "true", "True")
    if "false" in x:
        x = handle_keywords(x, "false", "False")
    if "throw" in x:
        x = handle_keywords(x, "throw", "raise")

    switch_match = SWITCH_PATTERN.match(x)
    if switch_match:
        switch_var = switch_match.group(1)
        switch_branch = 0
        return ""

    switch_match = CASE_PATTERN.match(x)
    if switch_match:
        indent = switch_match.group(1)
        value = switch_match.group(2).replace("::", ".")
        cond = "if" if switch_branch == 0 else "elif"
        switch_branch += 1
        return f"{indent}{cond} {switch_var} == {value}:"

    switch_match = DEFAULT_PATTERN.match(x)
    if switch_match:
        indent = switch_match.group(1)
        return f"{indent}else:"

    # handle 'void Class::method(...)' and 'void method(...)'
    if VOID_METHOD_PATTERN.search(x):
        x = handle_void_functions(x)

    # 'Q*::' -> 'Q*.'
    if QT_QUALIFIER_PATTERN.search(x):
        x = x.replace("::", ".")

    # handle 'nullptr'
    if "nullptr" in x:
        x = x.replace("nullptr", "None")

    ## Special Cases Rules
    xs = x.strip()
    # Special case for 'main'
    if xs.startswith("int main("):
        return f'{get_indent(x)}if __name__ == "__main__":'

    if xs.startswith("QApplication app(argc, argv)"):
        return f"{get_indent(x)}app = QApplication([])"

    # Special case for 'return app.exec()'
    if xs.startswith("return app.exec"):
        return x.replace("return app.exec()", "sys.exit(app.exec())")

    # Handle includes -> import
    if xs.startswith("#include"):
        x = handle_include(x)
        return dstrip(x)

    if xs.startswith("emit "):
        x = handle_emit(x)
        return dstrip(x)

    # *_cast
    if "_cast<" in x:
        x = handle_casts(x)
        xs = x.strip()

    # Handle Qt classes that needs to be removed
    x = handle_useless_qt_classes(x)

    # Handling ternary operator
    if TERNARY_OPERATOR_PATTERN.search(xs):
        x = x.replace(" ? ", " if ")
        x = x.replace(" : ", " else ")
        xs = x.strip()

    # Handle 'while', 'if', and 'else if'
    # line might end in ')' or ") {"
    if xs.startswith(("while", "if", "else if", "} else if")):
        x = handle_conditions(x)
        return dstrip(x)
    elif ELSE_PATTERN.search(x):
        x = ELSE_REPLACEMENT_PATTERN.sub("else:", x)
        return dstrip(x)

    # 'cout' and 'endl'
    if COUT_PATTERN.search(x) or ("endl" in x) or xs.startswith("qDebug()"):
        x = handle_cout_endl(x)
        return dstrip(x)

    # 'for' loops
    if FOR_PATTERN.search(xs):
        return dstrip(handle_for(x))

    # 'foreach' loops
    if FOREACH_PATTERN.search(xs):
        return dstrip(handle_foreach(x))

    # 'class' and 'structs'
    if CLASS_PATTERN.search(x) or STRUCT_PATTERN.search(x):
        if "struct " in x:
            x = x.replace("struct ", "class ")
        return handle_class(x)

    # 'delete'
    if DELETE_PATTERN.search(x):
        return x.replace("delete", "del")

    # 'public:', etc
    if xs in QUALIFIERS:
        return f"# {x}".replace(":", "")

    # For expressions like: `Type var`
    # which does not contain a `= something` on the right side
    # should match
    #     Some thing
    #     QSome<var> thing
    #     QSome thing(...)
    # should not match
    #     QSome thing = a
    #     QSome thing = a(...)
    #     def something(a, b, c)
    # At the end we skip methods with the form:
    #     QStringView Message::body()
    # to threat them as methods.
    if (has_semicolon and VAR1_PATTERN.search(xs)
            and not ([f for f in FUNCTION_QUALIFIERS if f in x])
            and xs.split()[0] not in ("def", "return", "and", "or")
            and not VAR2_PATTERN.search(xs)
            and ("{" not in x and "}" not in x)):

        # FIXME: this 'if' is a hack for a function declaration with this form:
        #   QString myDecoderFunc(QByteArray &localFileName)
        # No idea how to check for different for variables like
        #   QString notAFunction(Something something)
        # Maybe checking the structure of the arguments?
        if "Func" not in x:
            return dstrip(handle_type_var_declaration(x))

    # For expressions like: `Type var = value`,
    # considering complex right-side expressions.
    #   QSome thing = b
    #   QSome thing = b(...)
    #   float v = 0.1
    #   QSome *thing = ...
    if (VAR3_PATTERN.search(xs)
            and ("{" not in x and "}" not in x)):
        left, right = x.split("=", 1)
        var_name = " ".join(left.strip().split()[1:])
        x = f"{get_indent(x)}{remove_ref(var_name)} = {right.strip()}"
        # Special case: When having this:
        #    QVBoxLayout *layout = new QVBoxLayout;
        # we end up like this:
        #    layout = QVBoxLayout
        # so we need to add '()' at the end if it's just a word
        # with only alpha numeric content
        if VAR4_PATTERN.search(xs) and not xs.endswith(")"):
            v = x.rstrip()
            if (not v.endswith(" True") and not v.endswith(" False")
                and not v.endswith(" None")):
                x = f"{v}()"
        return dstrip(x)

    # For constructors, that we now the shape is:
    #    ClassName::ClassName(...)
    if CONSTRUCTOR_PATTERN.search(xs):
        x = handle_constructors(x)
        return dstrip(x)

    # For base object constructor:
    #       : QWidget(parent)
    if (
        xs.startswith(": ")
        and ("<<" not in x)
        and ("::" not in x)
        and not xs.endswith(";")
    ):

        return handle_constructor_default_values(x)

    # Arrays declarations with the form:
    #   type var_name[] = {...
    #   type var_name {...
    # if re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+\[\] * = *\{", x.strip()):
    if ARRAY_VAR_PATTERN.search(xs):
        x = handle_array_declarations(x)
        xs = x.strip()

    # Methods with return type
    #     int Class::method(...)
    #     QStringView Message::body()
    if RETURN_TYPE_PATTERN.search(xs):
        # We just need to capture the 'method name' and 'arguments'
        x = handle_methods_return_type(x)
        xs = x.strip()

    # Handling functions
    # By this section of the function, we cover all the other cases
    # So we can safely assume it's not a variable declaration
    if FUNCTION_PATTERN.search(xs):
        x = handle_functions(x)
        xs = x.strip()

    # if it is a C++ iterator declaration, then ignore it due to dynamic typing in Python
    # eg: std::vector<int> it;
    # the case of iterator being used inside a for loop is already handed in handle_for(..)
    # TODO: handle iterator initialization statement like it = container.begin();
    if ITERATOR_PATTERN.search(x):
        x = ""
        return x

    # By now all the typical special considerations of scope resolution operator should be handled
    # 'Namespace*::' -> 'Namespace*.'
    # TODO: In the case where a C++ class function is defined outside the class, this would be wrong
    # but we do not have such a code snippet yet
    if SCOPE_PATTERN.search(x):
        x = x.replace("::", ".")

    # General return for no special cases
    return dstrip(x)

    # TODO:
    # * Lambda expressions

    # * operator overload
    #    void operator()(int newState) { state = newState; }
    #    const QDBusArgument &operator>>(const QDBusArgument &argument, MyDictionary &myDict)
    #    inline bool operator==(const Employee &e1, const Employee &e2)
    #    void *operator new[](size_t size)

    # * extern "C" ...
    #    extern "C" MY_EXPORT int avg(int a, int b)

    # * typedef ...
    #    typedef int (*AvgFunction)(int, int);

    # * function pointers
    #    typedef void (*MyPrototype)();
