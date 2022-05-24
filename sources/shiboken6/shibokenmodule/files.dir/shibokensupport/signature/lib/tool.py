# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
tool.py

Some useful stuff, see below.
On the function with_metaclass see the answer from Martijn Pieters on
https://stackoverflow.com/questions/18513821/python-metaclass-understanding-the-with-metaclass
"""

from inspect import currentframe
from textwrap import dedent


def build_brace_pattern(level, separators):
    """
    Build a brace pattern upto a given depth

    The brace pattern parses any pattern with round, square, curly, or angle
    brackets. Inside those brackets, any characters are allowed.

    The structure is quite simple and is recursively repeated as needed.
    When separators are given, the match stops at that separator.

    Reason to use this instead of some Python function:
    The resulting regex is _very_ fast!

    A faster replacement would be written in C, but this solution is
    sufficient when the nesting level is not too large.

    Because of the recursive nature of the pattern, the size grows by a factor
    of 4 at every level, as does the creation time. Up to a level of 6, this
    is below 10 ms.

    There are other regex engines available which allow recursive patterns,
    avoiding this problem completely. It might be considered to switch to
    such an engine if the external module is not a problem.
    """
    assert type(separators) is str

    def escape(txt):
        return "".join("\\" + c for c in txt)

    ro, rc = round_ = "()"
    so, sc = square = "[]"
    co, cc = curly  = "CD"      # we insert "{}", later...
    ao, ac = angle  = "<>"
    q2, bs, q1 = '"', "\\", "'"
    allpat = round_ + square + curly + angle
    __ = "  "
    ro, rc, so, sc, co, cc, ao, ac, separators, q2, bs, q1, allpat = map(
        escape, (ro, rc, so, sc, co, cc, ao, ac, separators, q2, bs, q1, allpat))

    no_brace_sep_q = fr"[^{allpat}{separators}{q2}{bs}{q1}]"
    no_quot2 = fr"(?: [^{q2}{bs}] | {bs}. )*"
    no_quot1 = fr"(?: [^{q1}{bs}] | {bs}. )*"
    pattern = dedent(r"""
        (
          (?: {__} {no_brace_sep_q}
            | {q2} {no_quot2} {q2}
            | {q1} {no_quot1} {q1}
            | {ro} {replacer} {rc}
            | {so} {replacer} {sc}
            | {co} {replacer} {cc}
            | {ao} {replacer} {ac}
          )+
        )
        """)
    no_braces_q = f"[^{allpat}{q2}{bs}{q1}]*"
    repeated = dedent(r"""
        {indent}  (?: {__} {no_braces_q}
        {indent}    | {q2} {no_quot2} {q2}
        {indent}    | {q1} {no_quot1} {q1}
        {indent}    | {ro} {replacer} {rc}
        {indent}    | {so} {replacer} {sc}
        {indent}    | {co} {replacer} {cc}
        {indent}    | {ao} {replacer} {ac}
        {indent}  )*
        """)
    for idx in range(level):
        pattern = pattern.format(replacer = repeated if idx < level-1 else no_braces_q,
                                 indent = idx * "    ", **locals())
    return pattern.replace("C", "{").replace("D", "}")


# Copied from the six module:
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(type):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

        @classmethod
        def __prepare__(cls, name, this_bases):
            return meta.__prepare__(name, bases)
    return type.__new__(metaclass, 'temporary_class', (), {})


# A handy tool that shows the current line number and indents.
def lno(level):
    lineno = currentframe().f_back.f_lineno
    spaces = level * "  "
    return f"{lineno}{spaces}"

# eof
