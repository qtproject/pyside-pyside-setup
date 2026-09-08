#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""No CPython API inside a state-lock transaction, checked at the source.

The binding asserts this at runtime: the CPython type helpers say
SBK_ASSERT_LOCK_NOT_HELD(State), so a path that reaches them from a
transaction aborts a debug build. That catches what runs. This catches what
is written, including the paths no test happens to take.

Locked regions are the body of every StateLockGuard scope and every function
whose name ends in "Locked". From there it follows calls: a helper that
calls a helper that calls PyObject_GetAttr() is reported with the path that
leads to it, because that is the one a reader has to see to fix it.

What it cannot see, and does not pretend to:

  * calls through a function pointer or a virtual - cpp_dtor, mi_init and
    the type-discovery hooks are exactly that, and they reach generated
    code. The contract puts them after the unlock and the runtime assertion
    in DeferredActions::run() is what holds them to it.
  * anything outside the files it was given. A call into Qt is a leaf here.
  * overloads: two functions of one name are one node.

Allowed inside a transaction: the handful of operations the contract permits
that happen to be spelled with a Py prefix. Each entry is there because
someone argued for it, not because it looked harmless.

    check_state_lock_scope.py [files...]     defaults to libshiboken
                                             and libpyside
    check_state_lock_scope.py --graph        also print the call paths

Exit 0 when clean, 1 when something Python-shaped sits in a transaction.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Reading a type's own storage is not a CPython call: PepType_SOTP() is a
# pointer offset into memory we allocated, and Py_TYPE() a field read. Both
# are how a transaction reads a fact it may not go and compute.
ALLOWED = {
    "PepType_SOTP", "Py_TYPE", "Py_REFCNT", "Py_SIZE",
    "PyObject_HEAD", "Py_ssize_t",
    # Comparing against a type object is an address comparison, and getting
    # the metatype is a field read. Both are how the lease classifies
    # without walking a hierarchy.
    "SbkObjectType_TypeF", "SbkObject_TypeF",
    # A pinning increment. An increment cannot run anything: only the last
    # decrement reaches a destructor, and taking a reference never blocks,
    # never calls back and never needs a safe point. It is also what makes
    # the transaction safe - the object it pins outlives the work that
    # happens after the unlock. Py_DECREF is deliberately not here.
    "Py_INCREF", "Py_XINCREF", "Py_NewRef",
}

# Functions the transaction is allowed to call but that run after it, or
# outside it by construction. Following them would report the work the
# contract explicitly puts on the far side of the unlock.
BARRIERS = {
    # DeferredActions::run() is what the transaction hands its destructors,
    # decrefs and callbacks to. It runs after the unlock and says so itself:
    # its first line is SBK_ASSERT_NO_RAW_LOCK().
    "run",
    # The plan is built under the lock and executed after it, in the caller.
    "runInvalidationPlan",
}

CPYTHON = re.compile(r"\b(Py[A-Za-z_]\w*|_Py[A-Za-z_]\w*|Pep[A-Za-z_]\w*)\s*\(")
ANY_CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
GUARD = re.compile(r"\bStateLockGuard\b")
# A definition, not a declaration: a name, an argument list, then a brace.
DEFINITION = re.compile(
    r"^[\w:<>,*&\[\] ]*?\b(\w+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{",
    re.M)
KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "sizeof",
            "assert", "static_cast", "reinterpret_cast", "const_cast",
            "dynamic_cast", "do", "else", "case"}


def block_end(lines: list[str], start: int) -> int:
    """The line where a block opened at or after `start` closes.

    For a function definition, whose opening brace is on the first line.
    """
    depth, seen = 0, False
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        seen = seen or "{" in lines[i]
        if seen and depth <= 0:
            return i
    return len(lines) - 1


def scope_end(lines: list[str], start: int) -> int:
    """The line where the block *containing* `start` closes.

    A guard declared as a local lives to the end of its enclosing scope, and
    that scope was opened before it - so the brace to look for is the one
    that takes the count below zero, not one that opens after it. Getting
    this wrong makes everything after the guard's own block look as if it
    ran under the lock, which is how this check first reported 1444 calls
    that were nothing of the sort.
    """
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth < 0:
            return i
    return len(lines) - 1


def gil_branch_lines(lines: list[str]) -> set[int]:
    """The lines that belong to a build with a GIL.

    Everything in the #else of an `#ifdef Py_GIL_DISABLED`. They are not part
    of the build this check is about, and reading them together with their
    free-threading twin is how a call graph grows edges that exist in
    neither: the two branches define the same function name twice.
    """
    gil, depth, in_ft, ft_depth = set(), 0, False, 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#if"):
            depth += 1
            if "Py_GIL_DISABLED" in stripped and not in_ft:
                in_ft, ft_depth = True, depth
                continue
        elif stripped.startswith("#else") and in_ft and depth == ft_depth:
            in_ft = False
            gil.add(i)
            for j in range(i + 1, len(lines)):
                s = lines[j].strip()
                if s.startswith("#if"):
                    depth += 1
                elif s.startswith("#endif"):
                    depth -= 1
                    if depth < ft_depth:
                        break
                gil.add(j)
            continue
        elif stripped.startswith("#endif"):
            depth -= 1
            if in_ft and depth < ft_depth:
                in_ft = False
    return gil


def functions(text: str) -> dict[str, list[list[str]]]:
    """Every function defined here, by name, as one entry per definition.

    One entry per definition and not one merged body: two functions of the
    same name would otherwise lend each other their calls, and the graph
    would report a path that exists in neither of them.
    """
    lines = text.splitlines()
    skip = gil_branch_lines(lines)
    result: dict[str, list[list[str]]] = {}
    for match in DEFINITION.finditer(text):
        name = match.group(1)
        if name in KEYWORDS:
            continue
        start = text[:match.start()].count("\n")
        if start in skip:
            continue
        result.setdefault(name, []).append(
            lines[start:block_end(lines, start) + 1])
    return result


def calls(body: list[str]) -> set[str]:
    found = set()
    for line in body:
        code = line.split("//")[0]
        found.update(name for name in ANY_CALL.findall(code)
                     if name not in KEYWORDS)
    return found


def cpython_calls(body: list[str]) -> list[tuple[int, str, str]]:
    found = []
    for offset, line in enumerate(body):
        code = line.split("//")[0]
        for name in CPYTHON.findall(code):
            if name not in ALLOWED:
                found.append((offset, name, line.strip()))
    return found


def locked_regions(text: str) -> list[tuple[list[str], str]]:
    """(body, what) for every region that runs under the state lock."""
    lines = text.splitlines()
    regions = []
    for i, line in enumerate(lines):
        before = line.split("StateLockGuard")[0]
        if GUARD.search(line) and "class" not in line and "//" not in before:
            regions.append((lines[i:scope_end(lines, i) + 1],
                            "a StateLockGuard scope"))
    # DEFINITION and not a looser pattern of its own: an indented *call* to
    # somethingLocked() reads like a definition to anything that does not
    # insist on the brace, and the region then swallows the rest of the
    # function around the call - which is a different function entirely.
    for match in DEFINITION.finditer(text):
        name = match.group(1)
        if not name.endswith("Locked") or name in KEYWORDS:
            continue
        start = text[:match.start()].count("\n")
        regions.append((lines[start:block_end(lines, start) + 1], f"{name}()"))
    return regions


def default_files() -> list[Path]:
    """Both runtime libraries, not just this one.

    libpyside takes the state lock as well - through the wrappers it hands
    to Qt - so a transaction written there has the same contract, and a
    check that only reads libshiboken says nothing about it.
    """
    libpyside = HERE.parents[1] / "pyside6" / "libpyside"
    files = sorted(HERE.glob("*.cpp"))
    if libpyside.is_dir():
        files += sorted(libpyside.glob("*.cpp"))
    return files


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_paths = "--graph" in sys.argv[1:]
    files = [Path(a) for a in args] or default_files()

    universe: dict[str, list[list[str]]] = {}
    owner: dict[str, str] = {}
    for path in files:
        for name, bodies in functions(path.read_text(errors="replace")).items():
            universe.setdefault(name, []).extend(bodies)
            owner.setdefault(name, path.name)

    problems: list[str] = []
    for path in files:
        text = path.read_text(errors="replace")
        if "StateLockGuard" not in text and "Locked(" not in text:
            continue
        lines = text.splitlines()
        for body, what in locked_regions(text):
            first = lines.index(body[0]) + 1 if body[0] in lines else 0
            # direct
            for offset, name, code in cpython_calls(body):
                problems.append(f"{path.name}:{first + offset}: {name}() "
                                f"directly inside {what}\n    {code}")
            # transitive
            seen, queue = set(), [(callee, [what]) for callee in calls(body)]
            while queue:
                name, path_here = queue.pop()
                # An allowed call is allowed whole: following into it would
                # report the very implementation that was argued about.
                if name in seen or name in ALLOWED or name in BARRIERS:
                    continue
                if name not in universe:
                    continue
                seen.add(name)
                trail = path_here + [f"{name}()"]
                for body in universe[name]:
                    for _, called, code in cpython_calls(body):
                        where = " -> ".join(trail) if show_paths else \
                            f"{trail[0]} -> ... -> {name}()"
                        problems.append(f"{owner[name]}: {called}() reached "
                                        f"from {where}\n    {code}")
                    queue += [(callee, trail) for callee in calls(body)]

    for problem in problems:
        print(problem)
    if problems:
        print(f"\n{len(problems)} CPython call(s) in or reachable from a "
              f"state-lock transaction. The lock is a leaf: prepare the fact "
              f"before it, or add the call to ALLOWED with a reason.")
        return 1
    print(f"clean: no CPython API in or reachable from a state-lock "
          f"transaction ({len(files)} files, {len(universe)} functions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
