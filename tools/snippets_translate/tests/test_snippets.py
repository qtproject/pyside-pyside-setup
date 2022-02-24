# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from main import get_snippets, get_snippet_ids


def test_stacking():
    lines = [
        "//! [A] //! [B] ",
        "//! [C] //! [D] //! [E]",
        "// Content",
        "//! [C] //! [A] ",
        "//! [B] //! [D] //! [E]",
    ]
    snippets = get_snippets(lines)
    assert len(snippets) == 5
    assert len(snippets[0]) == 4  # A starts at line 0 and ends at line 3
    assert len(snippets[1]) == 5  # B starts at line 0 and ends at line 4
    assert len(snippets[2]) == 3  # C starts at line 1 and ends at line 3
    assert len(snippets[3]) == 4  # D starts at line 1 and ends at line 4
    assert len(snippets[4]) == 4  # E starts at line 1 and ends at line 4


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
    snippets = get_snippets(lines)
    assert len(snippets) == 3

    assert len(snippets[0]) == 5
    assert snippets[0] == lines[:5]

    assert len(snippets[1]) == 6
    assert snippets[1] == lines[1:]

    assert len(snippets[2]) == 4
    assert snippets[2] == lines[2:6]


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
    snippets = get_snippets(lines)
    assert len(snippets) == 3

    assert len(snippets[0]) == 4
    assert snippets[0] == lines[1:5]

    assert len(snippets[1]) == 7
    assert snippets[1] == lines[3:]

    assert len(snippets[2]) == 4
    assert snippets[2] == lines[4:8]


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

    snippets = get_snippets(lines)
    assert len(snippets) == 2

    assert len(snippets[0]) == 3
    assert snippets[0] == lines[1:4]

    assert len(snippets[1]) == 4
    assert snippets[1] == lines[3:7]


def test_snippet_ids():
    assert get_snippet_ids("") == []
    assert get_snippet_ids("//! ") == []  # Invalid id
    assert get_snippet_ids("//! [some name]") == ["some name"]
    assert get_snippet_ids("//! [some name] [some other name]") == ["some name"]
    assert get_snippet_ids("//! [some name] //! ") == ["some name"]  # Invalid id
    assert get_snippet_ids("//! [some name] //! [some other name]") == ["some name", "some other name"]
