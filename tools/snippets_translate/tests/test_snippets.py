# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from main import _get_snippets, get_snippet_ids, CPP_SNIPPET_PATTERN


C_COMMENT = "//"


def test_stacking():
    lines = [
        "//! [A] //! [B] ",
        "//! [C] //! [D] //! [E]",
        "// Content",
        "//! [C] //! [A] ",
        "//! [B] //! [D] //! [E]",
    ]
    snippets = _get_snippets(lines, C_COMMENT, CPP_SNIPPET_PATTERN)
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
    snippets = _get_snippets(lines, C_COMMENT, CPP_SNIPPET_PATTERN)
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
    a_id = "//! [A]"
    b_id = "//! [B]"
    lines = [
        "pretext",
        a_id,
        "l1",
        "//! [C]",
        "//! [A] //! [B]",
        "l2",
        "l3 // Comment",
        b_id,
        "posttext",
        "//! [C]",
    ]
    snippets = _get_snippets(lines, C_COMMENT, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 3

    # Simple snippet ID lines are generated
    snippet_a = snippets["A"]
    assert len(snippet_a) == 4
    assert snippet_a == lines[1:4] + [a_id]

    snippet_c = snippets["C"]
    assert len(snippet_c) == 7
    assert snippet_c == lines[3:]

    snippet_b = snippets["B"]
    assert len(snippet_b) == 4
    assert snippet_b == [b_id] + lines[5:8]


def test_snippets():
    a_id = "//! [A]"
    b_id = "//! [B]"

    lines = [
        "pretext",
        a_id,
        "l1",
        "//! [A] //! [B]",
        "l2",
        "l3 // Comment",
        b_id,
        "posttext"
    ]

    snippets = _get_snippets(lines, C_COMMENT, CPP_SNIPPET_PATTERN)
    assert len(snippets) == 2

    snippet_a = snippets["A"]

    assert len(snippet_a) == 3
    assert snippet_a == lines[1:3] + [a_id]

    snippet_b = snippets["B"]
    assert len(snippet_b) == 4
    assert snippet_b == [b_id] + lines[4:7]


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
