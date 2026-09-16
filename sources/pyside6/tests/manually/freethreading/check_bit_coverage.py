#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""Every option bit is demonstrated, and every demonstration names a bit.

  1. Every bit has a counter-proof that clears it, or an entry in
     DEMONSTRATED_ELSEWHERE with the reason.
  2. Every counter-proof clears a bit the enum has.
  3. The subject of every counter-proof is itself an entry, so it also runs
     with the bit set.
  4. Entries are counter-proofs plus subjects, and subjects are the test_*
     functions.

    check_bit_coverage.py [sbkftoptions.h] [failpoints.py]

Exit 0 when the four hold, 1 when one does not.
See README.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ftoptions                                                # noqa: E402

# The header path ftoptions.py uses.
HEADER = ftoptions.HEADER
TESTS_FILE = HERE / "failpoints.py"

# Bits demonstrated by something other than a counter-proof, each with its
# reason.
# See "Switching the locks off" in the free-threading notes.
DEMONSTRATED_ELSEWHERE = {
    "LazyTypeLock": "A/B in run.py's scenario table",
    "StateLock": "A/B in run.py's scenario table",
    "CallGuard": "A/B in run.py's scenario table",
    "MiOffsetsOnce": "a sanitizer A/B, and can have nothing else",
    "PostRoutineBatch": "its own scenario, post_routine_batch.py",
}


def tests_table(path: Path) -> tuple[dict, set]:
    """The TESTS mapping and the test_* functions, out of the syntax tree."""
    tree = ast.parse(path.read_text())
    table, functions = {}, set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            functions.add(node.name)
        if isinstance(node, ast.Assign) and any(
                getattr(target, "id", "") == "TESTS" for target in node.targets):
            for key, value in zip(node.value.keys, node.value.values):
                table[key.value] = value
    return table, functions


def counterproofs(node: ast.AST) -> list[tuple[list, str | None]]:
    """Every counterproof() call under node, as (positional args, context)."""
    found = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        if getattr(sub.func, "id", "") != "counterproof":
            continue
        args = [a.value if isinstance(a, ast.Constant) else None
                for a in sub.args]
        context = next((k.value.value for k in sub.keywords
                        if k.arg == "context" and isinstance(k.value, ast.Constant)),
                       None)
        found.append((args, context))
    return found


def main() -> int:
    header = Path(sys.argv[1]) if len(sys.argv) > 1 else HEADER
    tests_path = Path(sys.argv[2]) if len(sys.argv) > 2 else TESTS_FILE
    bits = ftoptions.option_bits(header)
    tests, functions = tests_table(tests_path)

    cleared: dict[str, list[str]] = {}
    complaints = []
    for name, node in tests.items():
        for args, context in counterproofs(node):
            for option in ([args[0]] if args else []) + ([context] if context else []):
                cleared.setdefault(option, []).append(name)
            if len(args) >= 2 and args[1] not in tests:
                complaints.append(f"{name} proves {args[1]!r}, which is not an entry")

    print(f"{len(bits)} bits, {len(tests)} entries, {len(functions)} test functions")

    for bit in bits:
        if bit not in cleared and bit not in DEMONSTRATED_ELSEWHERE:
            complaints.append(f"{bit} = {bits[bit]:#x} has no counter-proof "
                              f"and no exemption")
        if bit in cleared and bit in DEMONSTRATED_ELSEWHERE:
            print(f"  note: {bit} has a counter-proof and an exemption - "
                  f"one of the two is out of date")
    # A note, not a failure: the bit may not be in this tree yet.
    for bit in DEMONSTRATED_ELSEWHERE:
        if bit not in bits:
            print(f"  note: {bit} is exempted but not in the enum - either it "
                  f"is not in this tree yet, or the exemption outlived it")
    for option, users in cleared.items():
        if option not in bits:
            complaints.append(f"{', '.join(users)} clears {option!r}, "
                              f"which the enum does not have")

    proving = {n for n in tests if counterproofs(tests[n])}
    subjects = len(tests) - len(proving)
    if subjects != len(functions):
        complaints.append(f"{len(tests)} entries - {len(proving)} counter-proofs "
                          f"= {subjects} subjects, but {len(functions)} functions")
    named = {n for n in tests if n.startswith("proof-")}
    complaints += [f"{n} is named proof-* but proves nothing"
                   for n in sorted(named - proving)]
    complaints += [f"{n} proves something but is not named proof-*"
                   for n in sorted(proving - named)]

    for line in complaints:
        print(f"  {line}")
    if not complaints:
        print(f"  clean: {len(cleared)} bits by counter-proof, "
              f"{len(DEMONSTRATED_ELSEWHERE)} elsewhere")
    return 1 if complaints else 0


if __name__ == "__main__":
    sys.exit(main())
