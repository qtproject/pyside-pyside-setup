#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
##
## $QT_BEGIN_LICENSE:COMM$
##
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## $QT_END_LICENSE$
##
#############################################################################

"""Tool to dump Python Tokens"""


import sys
import tokenize


def format_token(t):
    r = repr(t)
    if r.startswith('TokenInfo('):
        r = r[10:]
    pos = r.find("), line='")
    if pos < 0:
        pos = r.find('), line="')
    if pos > 0:
        r = r[:pos + 1]
    return r


def first_non_space(s):
    for i, c in enumerate(s):
        if c != ' ':
            return i
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify file Name")
        sys.exit(1)
    filename = sys.argv[1]
    indent_level = 0
    indent = ''
    last_line_number = -1
    with tokenize.open(filename) as f:
        generator = tokenize.generate_tokens(f.readline)
        for t in generator:
            line_number = t.start[0]
            if line_number != last_line_number:
                code_line = t.line.rstrip()
                non_space = first_non_space(code_line)
                print('{:04d} {}{}'.format(line_number, '_' * non_space,
                                           code_line[non_space:]))
                last_line_number = line_number
            if t.type == tokenize.INDENT:
                indent_level = indent_level + 1
                indent = '    ' * indent_level
            elif t.type == tokenize.DEDENT:
                indent_level = indent_level - 1
                indent = '    ' * indent_level
            else:
                print('       ', indent, format_token(t))
