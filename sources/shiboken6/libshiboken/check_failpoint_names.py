#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""Every SBK_FAILPOINT() name is in KnownFailpoints, and the other way round.

A name that is not in the list is inert: nothing can arm it, armFailpoint()
answers false, and the test that wanted it reports a skip. A skip is not a
failure, so the row goes green in the one place where it demonstrates
nothing - which is how a new failpoint was shipped unarmable once already.

The reverse direction matters as much: a name in the list with no call site
is a point tests can arm and no thread will ever reach, so a test parked on
it waits out its timeout and calls that a hang.

    check_failpoint_names.py [files...]      defaults to libshiboken
                                             and libpyside

Exit 0 when the two sides agree, 1 when they do not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "sbkfailpoint.cpp"

# The array literal, and the string literals inside it. Deliberately not a
# C++ parse: the point is to read what the compiler reads, and this file has
# one such array.
KNOWN_ARRAY = re.compile(r"KnownFailpoints\s*=\s*\{(.*?)\};", re.DOTALL)
CALL_SITE = re.compile(r'SBK_FAILPOINT\s*\(\s*"([^"]+)"\s*\)')
LITERAL = re.compile(r'"([^"]+)"')


def registered() -> set[str]:
    text = REGISTRY.read_text(encoding="utf-8")
    # Two arrays: the free-threading one and the empty one a GIL build gets.
    return {name
            for body in KNOWN_ARRAY.findall(text)
            for name in LITERAL.findall(body)}


def called(files: list[Path]) -> dict[str, str]:
    """Name to the first place it is used, for the message."""
    used: dict[str, str] = {}
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name in CALL_SITE.findall(line):
                used.setdefault(name, f"{path.name}:{number}")
    return used


def default_files() -> list[Path]:
    """Every runtime library, not just the one the registry lives in.

    A file the check does not read looks like a name nobody reaches, so a
    failpoint placed in a library nobody listed ships unarmable - which is
    the thing this script exists to prevent. The set is therefore globbed
    rather than named: a list written out, here or in CMake, goes stale
    the next time a library is added, and a stale list fails silently.
    """
    sources = HERE.parents[1]
    return sorted(f
                  for directory in sorted(sources.glob("*/lib*"))
                  if directory.is_dir()
                  for f in directory.glob("*.cpp"))


def main() -> int:
    files = [Path(a) for a in sys.argv[1:]] or default_files()

    known = registered()
    used = called(files)

    problems = []
    for name, where in sorted(used.items()):
        if name not in known:
            problems.append(f"{where}: \"{name}\" is not in KnownFailpoints, so "
                            f"nothing can arm it and every test for it skips")
    for name in sorted(known - set(used)):
        problems.append(f"{REGISTRY.name}: \"{name}\" has no SBK_FAILPOINT() call "
                        f"site, so a test parked on it waits out its timeout")

    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"clean: {len(known)} failpoint(s), each registered and each reached "
          f"({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
