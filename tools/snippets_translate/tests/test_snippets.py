# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from main import get_snippets


SNIPPETS = ["pretext",
            "//![some name]", "line1",
            "//! [some name] [some other name]",
            "line2",
            "//! [some other name]",
            "posttext"]


def test_snippets():
    extracted = get_snippets(SNIPPETS)
    assert len(extracted) == len(SNIPPETS) - 2
