# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import re
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from shiboken6 import Shiboken

from shibokensupport.signature.lib.tool import build_brace_pattern

"""
This test tests the brace pattern from signature.lib.tool
against a slower reference implementation.
The pattern is crucial, because it is used heavily in signature.parser .
"""

# A slow reference parser for braces and strings
def check(s):
    open, close = "[{(<", "]})>"
    escape, quote = "\\", '"'
    instring = blind = False
    stack = []
    for c in s:
        if instring:
            if blind:
                blind = False
            elif c == escape:
                blind = True
            elif c == quote:
                instring = False
                stack.pop()
            continue
        if c in open:
            stack.append(c)
        elif c in close:
            pos = close.index(c)
            if ((len(stack) > 0) and
                (open[pos] == stack[len(stack)-1])):
                stack.pop()
            else:
                return False
        elif c == escape:
            return False
        elif c == quote:
            instring = True
            stack.append(c)
    return len(stack) == 0


class TestBracePattern(unittest.TestCase):
    tests = [
        (r'{[]{()}}', True),
        (r'[{}{})(]', False),
        (r'[{}{} ")(" ]', True),
        (r'[{}{} ")(\" ]', False),
        (r'[{}{} ")(\" ]"]', True),
        (r'a < b ( c [ d { "} \"\"}" } ] ) >', True),
        (r'a < b ( c [ d {  } ] ) >', True),
        (r'a < b ( c [ d { "huh" } ] ) >', True),
        (r'a < b ( c [ d { "huh\" \" \\\"" } ] ) >', True),
    ]

    def test_checkfunc(self):
        for test, result in self.tests:
            if result:
                self.assertTrue(check(test))
            else:
                self.assertFalse(check(test))

    def test_the_brace_pattern(self):
        func = re.compile(build_brace_pattern(5, ",") + "$", re.VERBOSE).match
        for test, result in self.tests:
            if result:
                self.assertTrue(func(test))
            else:
                self.assertFalse(func(test))


if __name__ == '__main__':
    unittest.main()
