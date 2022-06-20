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
                      handle_void_functions)
from parse_utils import dstrip, get_indent, remove_ref


def snippet_translate(x):

    ## Cases which are not C++
    ## TODO: Maybe expand this with lines that doesn't need to be translated
    if x.strip().startswith("content-type: text/html"):
        return x

    ## General Rules

    # Remove ';' at the end of the lines
    if x.endswith(";"):
        x = x[:-1]

    # Remove lines with only '{' or '}'
    if x.strip() == "{" or x.strip() == "}":
        return ""

    # Skip lines with the snippet related identifier '//!'
    if x.strip().startswith("//!"):
        return x

    # handle lines with only comments using '//'
    if x.lstrip().startswith("//"):
        x = x.replace("//", "#", 1)
        return x

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
        x = x.replace("new ", "")

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

    # handle 'void Class::method(...)' and 'void method(...)'
    if re.search(r"^ *void *[\w\_]+(::)?[\w\d\_]+\(", x):
        x = handle_void_functions(x)

    # 'Q*::' -> 'Q*.'
    if re.search(r"Q[\w]+::", x):
        x = x.replace("::", ".")

    # handle 'nullptr'
    if "nullptr" in x:
        x = x.replace("nullptr", "None")

    ## Special Cases Rules

    # Special case for 'main'
    if x.strip().startswith("int main("):
        return f'{get_indent(x)}if __name__ == "__main__":'

    if x.strip().startswith("QApplication app(argc, argv)"):
        return f"{get_indent(x)}app = QApplication([])"

    # Special case for 'return app.exec()'
    if x.strip().startswith("return app.exec"):
        return x.replace("return app.exec()", "sys.exit(app.exec())")

    # Handle includes -> import
    if x.strip().startswith("#include"):
        x = handle_include(x)
        return dstrip(x)

    if x.strip().startswith("emit "):
        x = handle_emit(x)
        return dstrip(x)

    # *_cast
    if "_cast<" in x:
        x = handle_casts(x)

    # Handle Qt classes that needs to be removed
    x = handle_useless_qt_classes(x)

    # Handling ternary operator
    if re.search(r"^.* \? .+ : .+$", x.strip()):
        x = x.replace(" ? ", " if ")
        x = x.replace(" : ", " else ")

    # Handle 'while', 'if', and 'else if'
    # line might end in ')' or ") {"
    if x.strip().startswith(("while", "if", "else if", "} else if")):
        x = handle_conditions(x)
        return dstrip(x)
    elif re.search("^ *}? *else *{?", x):
        x = re.sub(r"}? *else *{?", "else:", x)
        return dstrip(x)

    # 'cout' and 'endl'
    if re.search("^ *(std::)?cout", x) or ("endl" in x) or x.lstrip().startswith("qDebug()"):
        x = handle_cout_endl(x)
        return dstrip(x)

    # 'for' loops
    if re.search(r"^ *for *\(", x.strip()):
        return dstrip(handle_for(x))

    # 'foreach' loops
    if re.search(r"^ *foreach *\(", x.strip()):
        return dstrip(handle_foreach(x))

    # 'class' and 'structs'
    if re.search(r"^ *class ", x) or re.search(r"^ *struct ", x):
        if "struct " in x:
            x = x.replace("struct ", "class ")
        return handle_class(x)

    # 'delete'
    if re.search(r"^ *delete ", x):
        return x.replace("delete", "del")

    # 'public:'
    if re.search(r"^public:$", x.strip()):
        return x.replace("public:", "# public")

    # 'private:'
    if re.search(r"^private:$", x.strip()):
        return x.replace("private:", "# private")

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
    if (re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*\&]+(\(.*?\))? ?(?!.*=|:).*$", x.strip())
            and x.strip().split()[0] not in ("def", "return", "and", "or")
            and not re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w]+::[\w\*\&]+\(.*\)$", x.strip())
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
    if (re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+ *= *[\w\.\"\']*(\(.*?\))?", x.strip())
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
        if re.search(r"\w+ = [A-Z]{1}\w+", x.strip()) and not x.strip().endswith(")"):
            x = f"{x.rstrip()}()"
        return dstrip(x)

    # For constructors, that we now the shape is:
    #    ClassName::ClassName(...)
    if re.search(r"^ *\w+::\w+\(.*?\)", x.strip()):
        x = handle_constructors(x)
        return dstrip(x)

    # For base object constructor:
    #       : QWidget(parent)
    if (
        x.strip().startswith(": ")
        and ("<<" not in x)
        and ("::" not in x)
        and not x.strip().endswith(";")
    ):

        return handle_constructor_default_values(x)

    # Arrays declarations with the form:
    #   type var_name[] = {...
    #   type var_name {...
    # if re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+\[\] * = *\{", x.strip()):
    if re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*]+\[?\]? * =? *\{", x.strip()):
        x = handle_array_declarations(x)

    # Methods with return type
    #     int Class::method(...)
    #     QStringView Message::body()
    if re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w]+::[\w\*\&]+\(.*\)$", x.strip()):
        # We just need to capture the 'method name' and 'arguments'
        x = handle_methods_return_type(x)

    # Handling functions
    # By this section of the function, we cover all the other cases
    # So we can safely assume it's not a variable declaration
    if re.search(r"^[a-zA-Z0-9]+(<.*?>)? [\w\*\&]+\(.*\)$", x.strip()):
        x = handle_functions(x)

    # if it is a C++ iterator declaration, then ignore it due to dynamic typing in Python
    # eg: std::vector<int> it;
    # the case of iterator being used inside a for loop is already handed in handle_for(..)
    # TODO: handle iterator initialization statement like it = container.begin();
    if re.search(r"(std::)?[\w]+<[\w]+>::(const_)?iterator", x):
        x = ""
        return x

    # By now all the typical special considerations of scope resolution operator should be handled
    # 'Namespace*::' -> 'Namespace*.'
    # TODO: In the case where a C++ class function is defined outside the class, this would be wrong
    # but we do not have such a code snippet yet
    if re.search(r"[\w]+::", x):
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
