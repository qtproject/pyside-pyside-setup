#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""Every failpoint name is in its inventory, and every inventory name is used.

A name that is not in its inventory is inert: nothing can arm it,
armFailpoint() or armFailpointThrow() answers false, and the test that wanted
it reports a skip. A skip is not a failure, so the row goes green in the one
place where it demonstrates nothing - which is how a new failpoint was
shipped unarmable once already.

The reverse direction matters as much: a name in an inventory with no call
site is a point tests can arm and no thread will ever reach, so a test parked
on it waits out its timeout and calls that a hang.

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

# The array literals, and the string literals inside them. Deliberately not a
# C++ parse: the point is to read what the compiler reads.
#
# The two kinds are checked apart: arming one as the other ends in an
# assertion or a hang at run time.
KINDS = {
    "park": (re.compile(r"KnownFailpoints\s*=\s*\{(.*?)\};", re.DOTALL),
             re.compile(r'SBK_FAILPOINT\s*\(\s*"([^"]+)"\s*\)')),
    "throw": (re.compile(r"KnownThrowFailpoints\s*=\s*\{(.*?)\};", re.DOTALL),
              re.compile(r'SBK_FAILPOINT_THROW\s*\(\s*"([^"]+)"\s*\)')),
}
LITERAL = re.compile(r'"([^"]+)"')


def registered(array: re.Pattern) -> set[str]:
    text = REGISTRY.read_text(encoding="utf-8")
    # Two arrays per kind: the free-threading one and the empty one a GIL
    # build gets.
    return {name
            for body in array.findall(text)
            for name in LITERAL.findall(body)}


def called(files: list[Path]) -> dict[str, dict[str, str]]:
    """Per kind: name to the first place it is used, in one pass over the files."""
    used: dict[str, dict[str, str]] = {kind: {} for kind in KINDS}
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for kind, (_, call_site) in KINDS.items():
                for name in call_site.findall(line):
                    used[kind].setdefault(name, f"{path.name}:{number}")
    return used


# Directories that hold no shipped runtime code. An exclusion list on
# purpose: a directory forgotten here costs a few files read for nothing, one
# forgotten in an inclusion list is silently not checked.
NOT_RUNTIME = {"tests", "doc", "shiboken6_generator"}


def default_files() -> list[Path]:
    """Everything under sources/ the runtime is built from, headers included.

    A file the check does not read hides its failpoints, which then ship
    unarmable. Headers count: SBK_FAILPOINT() in an inline function is a
    call site like any other.
    """
    sources = HERE.parents[1]
    return sorted(f
                  for pattern in ("*.cpp", "*.h")
                  for f in sources.rglob(pattern)
                  if not NOT_RUNTIME & set(f.relative_to(sources).parts))


def main() -> int:
    files = [Path(a) for a in sys.argv[1:]] or default_files()

    problems = []
    total = 0
    seen = called(files)
    for kind, (array, _) in KINDS.items():
        known = registered(array)
        used = seen[kind]
        total += len(known)
        for name, where in sorted(used.items()):
            if name not in known:
                problems.append(f"{where}: \"{name}\" is not a {kind} failpoint, "
                                f"so nothing can arm it and every test for it "
                                f"skips")
        for name in sorted(known - set(used)):
            problems.append(f"{REGISTRY.name}: \"{name}\" is a {kind} failpoint "
                            f"with no call site, so a test that arms it waits "
                            f"out its timeout")

    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"clean: {total} failpoint(s), each registered and each reached "
          f"({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
