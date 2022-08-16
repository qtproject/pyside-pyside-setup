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

from main import _get_snippets, get_snippet_ids, CPP_SNIPPET_PATTERN


def test_stacking():
    lines = [
        "//! [A] //! [B] ",
        "//! [C] //! [D] //! [E]",
        "// Content",
        "//! [C] //! [A] ",
        "//! [B] //! [D] //! [E]",
    ]
    snippets = _get_snippets(lines, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 5

    snippet_a = snippets["A"]
    assert len(snippet_a) == 4  # A starts at line 0 and ends at line 3

    snippet_b = snippets["B"]
    assert len(snippet_b) == 5  # B starts at line 0 and ends at line 4

    snippet_c = snippets["C"]
    assert len(snippet_c) == 3  # C starts at line 1 and ends at line 3

    snippet_d = snippets["D"]
    assert len(snippet_d) == 4  # D starts at line 1 and ends at line 4

    snippet_e = snippets["E"]
    assert len(snippet_e) == 4  # E starts at line 1 and ends at line 4


def test_nesting():
    lines = [
        "//! [A]",
        "//! [B]",
        "//! [C]",
        "// Content",
        "//! [A]",
        "//! [C]",
        "//! [B]",
    ]
    snippets = _get_snippets(lines, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 3

    snippet_a = snippets["A"]
    assert len(snippet_a) == 5
    assert snippet_a == lines[:5]

    snippet_b = snippets["B"]
    assert len(snippet_b) == 6
    assert snippet_b == lines[1:]

    snippet_c = snippets["C"]
    assert len(snippet_c) == 4
    assert snippet_c == lines[2:6]


def test_overlapping():
    lines = [
        "pretext",
        "//! [A]",
        "l1",
        "//! [C]",
        "//! [A] //! [B]",
        "l2",
        "l3 // Comment",
        "//! [B]",
        "posttext",
        "//! [C]",
    ]
    snippets = _get_snippets(lines, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 3

    snippet_a = snippets["A"]
    assert len(snippet_a) == 4
    assert snippet_a == lines[1:5]

    snippet_c = snippets["C"]
    assert len(snippet_c) == 7
    assert snippet_c == lines[3:]

    snippet_b = snippets["B"]
    assert len(snippet_b) == 4
    assert snippet_b == lines[4:8]


def test_snippets():
    lines = [
        "pretext",
        "//! [A]",
        "l1",
        "//! [A] //! [B]",
        "l2",
        "l3 // Comment",
        "//! [B]",
        "posttext"
    ]

    snippets = _get_snippets(lines, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 2

    snippet_a = snippets["A"]
    assert len(snippet_a) == 3
    assert snippet_a == lines[1:4]

    snippet_b = snippets["B"]
    assert len(snippet_b) == 4
    assert snippet_b == lines[3:7]


def test_snippet_ids():
    assert get_snippet_ids("", CPP_SNIPPET_PATTERN) == []
    assert get_snippet_ids("//! ",
                           CPP_SNIPPET_PATTERN) == []  # Invalid id
    assert get_snippet_ids("//! [some name]",
                           CPP_SNIPPET_PATTERN) == ["some name"]
    assert get_snippet_ids("//! [some name] [some other name]",
                           CPP_SNIPPET_PATTERN) == ["some name"]
    assert get_snippet_ids("//! [some name] //! ",
                           CPP_SNIPPET_PATTERN) == ["some name"]  # Invalid id
    assert get_snippet_ids("//! [some name] //! [some other name]",
                           CPP_SNIPPET_PATTERN) == ["some name", "some other name"]
