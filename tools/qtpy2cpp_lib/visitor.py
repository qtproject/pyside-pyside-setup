# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""AST visitor printing out C++"""

import ast
import sys
import tokenize
import warnings

from .formatter import (CppFormatter, format_for_loop, format_literal,
                        format_reference, format_start_function_call,
                        write_import, write_import_from)
from .nodedump import debug_format_node


class ConvertVisitor(ast.NodeVisitor, CppFormatter):
    """AST visitor printing out C++
    Note on implementation:
    - Any visit_XXX() overridden function should call self.generic_visit(node)
      to continue visiting
    - When controlling the visiting manually (cf visit_Call()),
      self.visit(child) needs to be called since that dispatches to
      visit_XXX(). This is usually done to prevent undesired output
      for example from references of calls, etc.
    """

    debug = False

    def __init__(self, file_name, output_file):
        ast.NodeVisitor.__init__(self)
        CppFormatter.__init__(self, output_file)
        self._file_name = file_name
        self._class_scope = []  # List of class names
        self._stack = []  # nodes
        self._debug_indent = 0

    @staticmethod
    def create_ast(filename):
        """Create an Abstract Syntax Tree on which a visitor can be run"""
        node = None
        with tokenize.open(filename) as file:
            node = ast.parse(file.read(), mode="exec")
        return node

    def generic_visit(self, node):
        parent = self._stack[-1] if self._stack else None
        if self.debug:
            self._debug_enter(node, parent)
        self._stack.append(node)
        try:
            super().generic_visit(node)
        except Exception as e:
            line_no = node.lineno if hasattr(node, 'lineno') else -1
            error_message = str(e)
            message = f'{self._file_name}:{line_no}: Error "{error_message}"'
            warnings.warn(message)
            self._output_file.write(f'\n// {error_message}\n')
        del self._stack[-1]
        if self.debug:
            self._debug_leave(node)

    def visit_Add(self, node):
        self.generic_visit(node)
        self._output_file.write(' + ')

    def visit_Assign(self, node):
        self._output_file.write('\n')
        self.INDENT()
        line_no = node.lineno if hasattr(node, 'lineno') else -1
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                w = f"{self._file_name}:{line_no}: List assignment not handled."
                warnings.warn(w)
            elif isinstance(target, ast.Subscript):
                w = f"{self._file_name}:{line_no}: Subscript assignment not handled."
                warnings.warn(w)
            else:
                self._output_file.write(format_reference(target))
                self._output_file.write(' = ')
        self.visit(node.value)
        self._output_file.write(';\n')

    def visit_Attribute(self, node):
        """Format a variable reference (cf visit_Name)"""
        self._output_file.write(format_reference(node))

    def visit_BinOp(self, node):
        # Parentheses are not exposed, so, every binary operation needs to
        # be enclosed by ().
        self._output_file.write('(')
        self.generic_visit(node)
        self._output_file.write(')')

    def visit_BitAnd(self, node):
        self.generic_visit(node)
        self._output_file.write(" & ")

    def visit_BitOr(self, node):
        self.generic_visit(node)
        self._output_file.write(" | ")

    def visit_Call(self, node):
        self._output_file.write(format_start_function_call(node))
        # Manually do visit(), skip the children of func
        for i, arg in enumerate(node.args):
            if i > 0:
                self._output_file.write(', ')
            self.visit(arg)
        self._output_file.write(')')

    def visit_ClassDef(self, node):
        # Manually do visit() to skip over base classes
        # and annotations
        self._class_scope.append(node.name)
        self.write_class_def(node)
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_line('};')
        del self._class_scope[-1]

    def visit_Eq(self, node):
        self.generic_visit(node)
        self._output_file.write(" == ")

    def visit_Expr(self, node):
        self._output_file.write('\n')
        self.INDENT()
        self.generic_visit(node)
        self._output_file.write(';\n')

    def visit_Gt(self, node):
        self.generic_visit(node)
        self._output_file.write(" > ")

    def visit_GtE(self, node):
        self.generic_visit(node)
        self._output_file.write(" >= ")

    def visit_For(self, node):
        # Manually do visit() to get the indentation right.
        # TODO: what about orelse?
        self.indent_line(format_for_loop(node))
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_line('}')

    def visit_FunctionDef(self, node):
        class_context = self._class_scope[-1] if self._class_scope else None
        self.write_function_def(node, class_context)
        self.indent()
        self.generic_visit(node)
        self.dedent()
        self.indent_line('}')

    def visit_If(self, node):
        # Manually do visit() to get the indentation right. Note:
        # elsif() is modelled as nested if.
        self.indent_string('if (')
        self.visit(node.test)
        self._output_file.write(') {\n')
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_string('}')
        if node.orelse:
            self._output_file.write(' else {\n')
            self.indent()
            for b in node.orelse:
                self.visit(b)
            self.dedent()
            self.indent_string('}')
        self._output_file.write('\n')

    def visit_Import(self, node):
        write_import(self._output_file, node)

    def visit_ImportFrom(self, node):
        write_import_from(self._output_file, node)

    def visit_List(self, node):
        # Manually do visit() to get separators right
        self._output_file.write('{')
        for i, el in enumerate(node.elts):
            if i > 0:
                self._output_file.write(', ')
            self.visit(el)
        self._output_file.write('}')

    def visit_LShift(self, node):
        self.generic_visit(node)
        self._output_file.write(" << ")

    def visit_Lt(self, node):
        self.generic_visit(node)
        self._output_file.write(" < ")

    def visit_LtE(self, node):
        self.generic_visit(node)
        self._output_file.write(" <= ")

    def visit_Mult(self, node):
        self.generic_visit(node)
        self._output_file.write(' * ')

    def visit_Name(self, node):
        """Format a variable reference (cf visit_Attribute)"""
        self._output_file.write(format_reference(node))

    def visit_NameConstant(self, node):
        self.generic_visit(node)
        if node.value is None:
            self._output_file.write('nullptr')
        elif not node.value:
            self._output_file.write('false')
        else:
            self._output_file.write('true')

    def visit_Not(self, node):
        self.generic_visit(node)
        self._output_file.write("!")

    def visit_NotEq(self, node):
        self.generic_visit(node)
        self._output_file.write(" != ")

    def visit_Num(self, node):
        self.generic_visit(node)
        self._output_file.write(format_literal(node))

    def visit_RShift(self, node):
        self.generic_visit(node)
        self._output_file.write(" >> ")

    def visit_Str(self, node):
        self.generic_visit(node)
        self._output_file.write(format_literal(node))

    def visit_UnOp(self, node):
        self.generic_visit(node)

    def _debug_enter(self, node, parent=None):
        message = '{}>generic_visit({})'.format('  ' * self ._debug_indent,
                                                debug_format_node(node))
        if parent:
            message += ', parent={}'.format(debug_format_node(parent))
        message += '\n'
        sys.stderr.write(message)
        self._debug_indent += 1

    def _debug_leave(self, node):
        self._debug_indent -= 1
        message = '{}<generic_visit({})\n'.format('  ' * self ._debug_indent,
                                                  type(node).__name__)
        sys.stderr.write(message)
