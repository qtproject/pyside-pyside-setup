#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""
The bits of PYSIDE6_OPTION_FT, read out of sbkftoptions.h.

There is one inventory of measures and it lives in the header. A copy kept by
hand goes stale, and a stale copy is invisible in a result: the run simply
describes different code than the one it names.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HEADER = (Path(__file__).resolve().parents[5] / "sources" / "shiboken6"
          / "libshiboken" / "sbkftoptions.h")


def option_bits(header: Path = HEADER) -> dict[str, int]:
    """Every name in `enum Option`, with its value."""
    body = header.read_text()
    start = body.find("enum Option")
    end = body.find("};", start)
    if start < 0 or end < 0:
        sys.exit(f"no enum Option in {header}")
    # No anchor at the end of the line: half the entries carry a trailing
    # ///< comment.
    found = re.findall(r"^\s*(\w+)\s*=\s*(0[xX][0-9a-fA-F]+|\d+)\s*,?",
                       body[start:end], re.MULTILINE)
    bits = {name: int(value, 0) for name, value in found}
    if not bits:
        sys.exit(f"no option bits in {header}")
    # Every bit is a distinct power of two and the set is contiguous, so a
    # line the pattern fails to see is caught here rather than silently
    # switching a measure off.
    values = sorted(bits.values())
    if values != [1 << i for i in range(len(values))]:
        sys.exit(f"option bits in {header} are not 1, 2, 4 ...: "
                 f"{[hex(v) for v in values]} - a line was missed, or the "
                 "enum stopped being a flag set")
    return bits


def all_bits(bits: dict[str, int] | None = None) -> int:
    """Every measure there is.

    Leaving PYSIDE6_OPTION_FT unset means the same to the header and is the
    better way to say it; this is for the places that need a number, which is
    only ever "all except one".
    """
    values = (bits or option_bits()).values()
    result = 0
    for value in values:
        result |= value
    return result


if __name__ == "__main__":
    for name, bit in option_bits().items():
        print(f"{name:20} {bit:#06x}")
