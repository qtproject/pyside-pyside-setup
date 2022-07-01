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
