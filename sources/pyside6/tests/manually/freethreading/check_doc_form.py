#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""The notes keep their form: one section per bit, and a budget.

The free-threading notes are four files: freethreading.md, the overview,
and freethreading-lifecycle.md, -types.md and -bindings.md beside it.

  1. Every option bit has exactly one section in the notes that
     claims it, in one of two forms - "Bit `Name`; cleared, ..." or
     "`Name` is the bit; cleared, ..." - and names its counter-proof in the
     same paragraph. Bits with no counter-proof are the ones
     check_bit_coverage.py exempts.
  2. No section claims two bits, and a section of the notes that names a
     bit no other section claims says it has none of its own.
  3. A section stays within its budget of text lines - blank lines are
     paragraph breaks, not prose - unless doc_form_allow.txt excuses it with
     a reason.
  4. Every line of that allow file is used, and excuses a section that is
     really over budget. A section that has been shortened since takes its
     excuse with it.
  5. Every reference a source file makes to a named section - the See form
     these notes use - points at a heading that is really there. A heading
     nobody points at is fine; pointing at one that moved is not. A See
     names the notes, not a file: which file a section is in is the notes'
     business.
  6. No heading is in two of the four files, so a See has one answer.
  7. Every link to a notes file, from the notes or from README.md, names a
     file that is one of the four and an anchor that is one of its headings.

    check_doc_form.py [README.md [overview lifecycle types bindings]]

Exit 0 when the seven hold, 1 when one does not.
See README.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ftoptions                                                # noqa: E402
import check_bit_coverage                                       # noqa: E402

DEVELOPER = HERE.parents[2] / "doc" / "developer"
README = HERE / "README.md"
ALLOW = HERE / "doc_form_allow.txt"

NOTES_BUDGET = 20
ENTRY_BUDGET = 15

# How doc_form_allow.txt and the links name the files, whatever they are
# called on the command line.
NOTES_NAMES = ("freethreading.md", "freethreading-lifecycle.md",
               "freethreading-types.md", "freethreading-bindings.md")
README_NAME = "README.md"

# A bit with no counter-proof cannot name one in its section either.
NO_COUNTERPROOF = check_bit_coverage.DEMONSTRATED_ELSEWHERE

CLAIM = re.compile(r"^(?:Bit `(\w+)`|`(\w+)` is the bit); cleared, ",
                   re.MULTILINE)
NO_BIT = re.compile(r"no (?:option )?bit", re.IGNORECASE)
# Any comment marker, /// and * included: the quoted title is the anchor.
SEE = re.compile(r'See "([^"]+)" in (?:the free-threading notes|README)')
SEE_FILE = re.compile(r'See "([^"]+)" in `?freethreading[\w-]*\.md')
LINK = re.compile(r'\]\((?:[./]*doc/developer/)?(freethreading[\w-]*\.md)(?:#([\w-]+))?\)')
SOURCES = HERE.parents[3]
READ = (".cpp", ".h", ".py", ".md")


def sections(text: str) -> list[tuple[str, list[str]]]:
    """(heading, body) for every heading down to ###, in file order."""
    found: list[tuple[str, list[str]]] = []
    heading, body = None, []
    for line in text.splitlines():
        if line.startswith("#") and not line.startswith("####"):
            if heading is not None:
                found.append((heading, body))
            heading, body = line, []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        found.append((heading, body))
    return found


def slug(heading: str) -> str:
    """The anchor MyST gives a heading (myst_heading_anchors, GitHub style)."""
    text = heading.lower().replace("`", "")
    return re.sub(r"[^\w\- ]", "", text).strip().replace(" ", "-")


def read_allow(path: Path) -> dict[tuple[str, str], str]:
    """{(file, heading): reason}, one per line, "file : heading : reason"."""
    entries: dict[tuple[str, str], str] = {}
    if not path.exists():
        return entries
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in line.split(":", 2)]
        if len(parts) != 3 or not parts[2]:
            sys.exit(f"{path}:{number}: want 'file : heading : reason'")
        entries[(parts[0], parts[1])] = parts[2]
    return entries


def main() -> int:
    readme_path = Path(sys.argv[1]) if len(sys.argv) > 1 else README
    notes = [Path(a) for a in sys.argv[2:]] or [DEVELOPER / n for n in NOTES_NAMES]
    if len(notes) != len(NOTES_NAMES):
        sys.exit(f"want the {len(NOTES_NAMES)} notes files, got {len(notes)}")
    bits = ftoptions.option_bits()
    allow = read_allow(ALLOW)
    used: set[tuple[str, str]] = set()
    complaints: list[str] = []
    claimed: dict[str, list[str]] = {}
    headings: set[str] = set()
    anchors: dict[str, set[str]] = {}
    in_file: dict[str, list[str]] = {}
    loose: list[tuple[str, list[str], bool]] = []
    counted = 0

    files = [(path, NOTES_BUDGET, name) for path, name in zip(notes, NOTES_NAMES)]
    files.append((readme_path, ENTRY_BUDGET, README_NAME))
    for path, budget, listed in files:
        is_notes = listed != README_NAME
        for heading, body in sections(path.read_text()):
            counted += 1
            text = "\n".join(body)
            lines = 1 + sum(1 for line in body if line.strip())  # + heading
            key = (listed, heading.lstrip("# ").strip())
            headings.add(key[1])
            if is_notes:
                anchors.setdefault(listed, set()).add(slug(key[1]))
                in_file.setdefault(key[1], []).append(listed)
            mine = [a or b for a, b in CLAIM.findall(text)]
            has_proof = "proof-" in text
            for bit in mine:
                claimed.setdefault(bit, []).append(key[1])
            named = [b for b in bits if re.search(rf"`{b}`", text)]
            if mine:
                for bit in mine:
                    if not has_proof and bit not in NO_COUNTERPROOF:
                        complaints.append(f"{key[1]!r} claims {bit} without "
                                          f"naming its counter-proof")
            elif named and is_notes:
                loose.append((key[1], named, bool(NO_BIT.search(text))))
            if len(mine) > 1:
                complaints.append(f"{key[1]!r} claims {', '.join(mine)} - "
                                  f"that is one section per bit twice over")
            if lines > budget:
                if key in allow:
                    used.add(key)
                else:
                    complaints.append(f"{key[1]!r} is {lines} text lines, "
                                      f"budget {budget}, and has no entry in "
                                      f"{ALLOW.name}")
            elif key in allow:
                used.add(key)
                complaints.append(f"{key[1]!r} is within budget now - drop "
                                  f"its line from {ALLOW.name}")

    print(f"{counted} sections, {len(bits)} bits, {len(allow)} allowed")

    for bit in bits:
        where = claimed.get(bit, [])
        if not where:
            complaints.append(f"{bit} has no section that claims it")
        if len(where) > 1:
            complaints.append(f"{bit} is claimed by {len(where)} sections: "
                              f"{', '.join(where)}")
    for title, named, says_none in loose:
        orphans = [b for b in named if b not in claimed]
        if orphans and not says_none:
            complaints.append(f"{title!r} names {', '.join(orphans)}, which "
                              f"no section claims, and does not say it has "
                              f"no bit of its own")
    for bit in claimed:
        if bit not in bits:
            complaints.append(f"a section claims {bit}, which the enum does "
                              f"not have")
    for title, where in in_file.items():
        if len(where) > 1:
            complaints.append(f"{title!r} is a heading in {', '.join(where)}")
    for path, _, listed in files:
        for target, anchor in LINK.findall(path.read_text()):
            if target not in anchors:
                complaints.append(f"{listed} links to {target}, which is not "
                                  f"one of the notes")
            elif anchor and anchor not in anchors[target]:
                complaints.append(f"{listed} links to {target}#{anchor}, "
                                  f"which is not a heading there")
    references = 0
    for path in sorted(SOURCES.rglob("*")):
        if path.suffix not in READ or not path.is_file():
            continue
        if any(part.startswith(("build", ".")) for part in path.parts):
            continue
        source = path.read_text(errors="replace")
        for title in SEE_FILE.findall(source):
            complaints.append(f"{path.name} sends {title!r} to a file - a See "
                              f"names the notes")
        for title in SEE.findall(source):
            references += 1
            if title not in headings:
                complaints.append(f"{path.name} points at {title!r}, which "
                                  f"is not a heading")
    print(f"  {references} references to a named section")

    for key in allow.keys() - used:
        complaints.append(f"{key[1]!r} in {ALLOW.name} is not a section of "
                          f"{key[0]}")

    for line in complaints:
        print(f"  {line}")
    if not complaints:
        print(f"  clean: {len(claimed)} bits with a section of their own")
    return 1 if complaints else 0


if __name__ == "__main__":
    sys.exit(main())
