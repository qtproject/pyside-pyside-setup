# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
fix-complaints.py

This module fixes the buildbot messages of external python files.
Run it once after copying a new version. It is idem-potent, unless
you are changing messages (what I did, of course :-) .
"""

import os
import glob
from pathlib import Path

patched_file_patterns = "backport_inspect.py typing27.py python_minilib_*.py"

offending_words = {
    "behavio""ur": "behavior",
    "at""least": "at_least",
    "reali""sed": "realized",
}

utf8_line = "# This Python file uses the following encoding: utf-8\n"
marker_line = f"# It has been edited by {Path(__file__).name} .\n"

def patch_file(fname):
    with fname.open() as f:
        lines = f.readlines()
    dup = lines[:]
    for idx, line in enumerate(lines):
        for word, repl in offending_words.items():
            if word in line:
                lines[idx] = line.replace(word, repl)
                print(f"line:{line!r} {word!r}->{repl!r}")
    if lines[0].strip() != utf8_line.strip():
        lines[:0] = [utf8_line, "\n"]
    if lines[1] != marker_line:
        lines[1:1] = marker_line
    if lines != dup:
        with open(fname, "w") as f:
            f.write("".join(lines))

def doit():
    dirname = Path(__file__).parent
    patched_files = []
    for name in patched_file_patterns.split():
        pattern = dirname / name
        patched_files += glob.glob(pattern)
    for fname in patched_files:
        print("Working on", fname)
        patch_file(fname)

if __name__ == "__main__":
    doit()

# end of file
