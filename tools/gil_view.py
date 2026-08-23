#!/usr/bin/env python3
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
"""Show the series through one build's eyes, with the conditionals resolved.

The free-threading work is supposed to leave a build with a GIL alone. That is
a claim a reviewer cannot check by reading a diff full of #ifdef - so resolve
them and let the text speak. unifdef(1) rewrites only the Py_GIL_DISABLED
conditionals and leaves every other line untouched, which is what makes the
result still readable; cpp -E would expand headers and macros and destroy it.

    gil_view.py                 GIL view of BASE vs HEAD - what the shipped
                                build actually gets out of the series
    gil_view.py --ft            FT view of HEAD - the free-threaded side with
                                no conditionals left, for reviewing the design
    gil_view.py --generated     the same over the generated wrappers in the
                                build tree, which is where the bulk sits

Writes plain diff/text files and prints their paths. Nothing to install.
"""

from __future__ import annotations

import argparse
import difflib
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_BASE = "@{upstream}"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", os.fspath(REPO), *args],
                          capture_output=True, text=True).stdout


FAILED: list[str] = []

DIRECTIVES = ("#if ", "#ifdef ", "#ifndef ", "#elif ")


def uncomment_conditionals(source: str) -> str:
    """Drop a trailing // comment from the Py_GIL_DISABLED directives.

    Only needed for -t, which switches comment parsing off: unifdef then reads
    "Py_GIL_DISABLED  // the GIL twin" as the expression and gives up on the
    whole line. The lines this touches are the ones that get resolved away.
    """
    lines = source.splitlines(keepends=True)
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if (stripped.startswith(DIRECTIVES) and "Py_GIL_DISABLED" in line
                and "//" in line):
            head = line.split("//", 1)[0]
            lines[i] = head.rstrip() + "\n"
    return "".join(lines)


def view(source: str, mode: str, what: str = "?") -> str:
    """Resolve the Py_GIL_DISABLED conditionals, leave the rest alone.

    Glue snippets are not valid C++ - they carry %CONVERTTOPYTHON[...] and
    apostrophes in prose - so unifdef's string and comment parsing chokes on
    them and it truncates its output. -t turns that parsing off. A silent
    fallback to the unfiltered source would report "no difference" for a file
    that was never filtered, which is worse than no answer at all.
    """
    flag = "-UPy_GIL_DISABLED" if mode == "gil" else "-DPy_GIL_DISABLED"
    reason = "not run"
    for args, text in (([flag, "-"], source),
                       (["-t", flag, "-"], uncomment_conditionals(source))):
        p = subprocess.run(["unifdef", *args], input=text,
                           capture_output=True, text=True)
        # unifdef: 0 = nothing to do, 1 = rewritten, anything else = error
        if p.returncode in (0, 1):
            return p.stdout
        err = p.stderr.strip().splitlines()
        reason = err[0] if err else str(p.returncode)
    FAILED.append(f"{what}: {reason}")
    return source


def sources(base: str, head: str) -> list[str]:
    spec = [base] if head == "-" else [f"{base}..{head}"]
    return [f for f in git("diff", "--name-only", *spec).split()
            if f.endswith((".h", ".cpp"))]


def build_dir(want: str | None = None) -> pathlib.Path | None:
    """A build tree recorded in build_history.

    build_dir.txt holds the tree on the first line and the configuration on
    the second, and the path already ends in /build - do not append it again.
    Without `want` this is the newest entry, which is only the right tree as
    long as nothing else was built since - so --build says which one, and the
    caller is told what was picked either way.
    """
    history = REPO / "build_history"
    stamps = sorted(history.glob("*/build_dir.txt")) if history.is_dir() else []
    for stamp in reversed(stamps):
        lines = stamp.read_text().splitlines()
        if want and (len(lines) < 2 or want not in lines[1]):
            continue
        tree = pathlib.Path(lines[0].strip())
        if tree.is_dir():
            return tree
    return None


def content(rev: str, path: str) -> str:
    """The file at a revision, or from the working tree for rev "-"."""
    return (REPO / path).read_text() if rev == "-" else git("show", f"{rev}:{path}")


def diff_series(base: str, head: str, mode: str, out: pathlib.Path) -> None:
    total, per_file = 0, []
    with out.open("w") as fp:
        for f in sources(base, head):
            a = view(content(base, f), mode, f)
            b = view(content(head, f), mode, f)
            d = list(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                          f"{base}:{f}", f"{head}:{f}",
                                          lineterm=""))
            n = sum(1 for line in d
                    if line[:1] in "+-" and line[:3] not in ("+++", "---"))
            if n:
                per_file.append((n, f))
                total += n
                fp.write("\n".join(d) + "\n\n")
    for n, f in sorted(per_file, reverse=True):
        print(f"{n:6d}  {f}")
    print(f"{total:6d}  changed lines in the {mode} view")
    report_failures()
    print(f"\n{out}")


def dump_head(base: str, head: str, mode: str, out: pathlib.Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for f in sources(base, head):
        target = out / f
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(view(content(head, f), mode, f))
    print(f"{mode} view of {head}: {out}")


def scan_generated(mode: str, want: str | None) -> None:
    bd = build_dir(want)
    if bd is None or not bd.is_dir():
        sys.exit(f"no build tree found for {want or 'the newest build'} - "
                 "build with --build-tests first")
    print(f"build tree: {bd}")
    marks = ("acquireWrapper", "AcquiredWrapper", "CallLease",
             "retrieveMetaObjectForCppObject", "wrapperInherits")
    files = held = lines = 0
    for p in bd.rglob("*_wrapper.cpp"):
        try:
            text = p.read_text()
        except OSError:
            continue
        if not any(m in text for m in marks):
            continue
        files += 1
        n = sum(1 for line in view(text, mode, p.name).splitlines()
                if any(m in line for m in marks))
        if n:
            held += 1
            lines += n
    print(f"generated wrappers naming the free-threading API: {files}")
    print(f"  of those, still naming it in the {mode} view:    {held}")
    print(f"  remaining lines:                                 {lines}")


def report_failures() -> None:
    if not FAILED:
        return
    print(f"\nunifdef could not resolve {len(FAILED)} file(s) - those numbers "
          f"mean nothing:", file=sys.stderr)
    for line in FAILED:
        print(f"  {line}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help="what to compare against (default: the tracked branch)")
    ap.add_argument("--head", default="HEAD",
                    help='a revision, or "-" for the working tree')
    ap.add_argument("--ft", action="store_true",
                    help="the free-threaded side instead of the GIL one")
    ap.add_argument("--generated", action="store_true",
                    help="scan the generated wrappers in the build tree")
    ap.add_argument("--build", metavar="CONFIG",
                    help="which build tree to scan, by its build_history "
                         "configuration line, e.g. py3.15 or py3.12-qt6.12.0; "
                         "default is the newest build, whatever that is")
    ap.add_argument("--dump", action="store_true",
                    help="write the resolved sources instead of a diff")
    args = ap.parse_args()

    if shutil.which("unifdef") is None:
        sys.exit("unifdef(1) not found")

    mode = "ft" if args.ft else "gil"
    if args.generated:
        scan_generated(mode, args.build)
        return 0

    out = REPO / "gil-view-out"
    out.mkdir(exist_ok=True)
    if args.dump:
        dump_head(args.base, args.head, mode, out / f"{mode}-view")
    else:
        diff_series(args.base, args.head, mode, out / f"{mode}-view.diff")
    return 0


if __name__ == "__main__":
    sys.exit(main())
