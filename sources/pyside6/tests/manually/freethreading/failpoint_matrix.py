#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""Run the failpoint tests on all three interpreters the review asks for.

A deterministic test is evidence only if it also passes where the race it
provokes cannot happen. So each of them runs on traditional CPython, on a
free-threaded binary with PYTHON_GIL=1, and on the same binary with
PYTHON_GIL=0. A test that only ever ran free-threaded proves that the code
works there, not that the fix is what makes it work.

Every test gets its own subprocess with a hard timeout. That is not tidiness:
these tests park a thread inside deallocation on purpose, so one of them
deadlocking must end as a failed cell and not as a run that never returns.
The child gets its own process group and is killed with it.

The rows are not interchangeable and are not guessed. A build directory
carries the Python version but not whether that Python was free-threaded -
`qfpdp-py3.15-...` is the same name for 3.15.0b3 and 3.15.0b3t - so each row
names its interpreter and its build, and the two are checked against each
other through the extension suffix before anything runs. A row without a
build is reported as missing, never silently dropped.

    FT_PYTHON     free-threaded interpreter   (default: the one running this)
    FT_BUILD_DIR  its build                   (default: newest in build_history)
    GIL_PYTHON    traditional interpreter     (no default)
    GIL_BUILD_DIR its build                   (no default)
    FAILPOINT_TIMEOUT   seconds per test, default 60

    failpoint_matrix.py                 every test, every row
    failpoint_matrix.py weakrefs        one test
    GIL_PYTHON=~/.pyenv/versions/3.13.3-debug/bin/python3 \
    GIL_BUILD_DIR=<build> failpoint_matrix.py

Exit: 0 all rows ran and all cells are clean, 1 something failed, 2 the setup
is wrong, 3 nothing failed but a row is missing - which is not yet the
evidence the validation plan asks for.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parents[5]
WORKER = Path(__file__).resolve().parent / "failpoints.py"

TIMEOUT = int(os.environ.get("FAILPOINT_TIMEOUT", "60"))
SKIP_RC = 77            # the worker's "no failpoints in this build"


class Row(NamedTuple):
    name: str
    python: str
    build: Path
    gil: bool           # what sys._is_gil_enabled() must say in the child


def latest_build_dir(python: str) -> Path:
    """The newest build this interpreter can actually load.

    Not simply the newest one: building the other row's interpreter makes it
    the newest, and the two differ by a suffix rather than by a directory
    name. Matching here turns a silently wrong row into no row at all.
    """
    wanted = interpreter_suffix(python)
    history = REPO / "build_history"
    entries = sorted(history.glob("*/build_dir.txt"),
                     key=lambda p: p.parent.name, reverse=True)
    seen = []
    for entry in entries:
        build = Path(entry.read_text().splitlines()[0])
        if not build.is_dir():
            continue
        seen.append(build)
        if build_suffix(build) == wanted:
            return build
    sys.exit(f"no build for {python} ({wanted}) in {history}; set "
             f"FT_BUILD_DIR. Seen: {', '.join(map(str, seen[:3])) or 'none'}")


def package_dir(build: Path) -> Path:
    return build.parent / "package_for_wheels"


def build_suffix(build: Path) -> str | None:
    """The extension suffix this build was compiled for, read off the
    Shiboken module it produced."""
    for so in package_dir(build).glob("shiboken6/Shiboken.*"):
        if so.suffix in (".so", ".pyd"):
            return so.name[len("Shiboken"):]
    return None


def interpreter_suffix(python: str) -> str | None:
    probe = "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
    try:
        out = subprocess.run([python, "-c", probe], capture_output=True,
                             text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def check(row: Row) -> str | None:
    """Why this row cannot run, or None if it can."""
    if not Path(row.build).is_dir():
        return f"no build at {row.build}"
    wanted = build_suffix(row.build)
    if wanted is None:
        return f"no Shiboken module under {package_dir(row.build)}"
    have = interpreter_suffix(row.python)
    if have is None:
        return f"cannot run {row.python}"
    if have != wanted:
        return f"{row.python} is {have}, build is {wanted}"
    return None


def rows() -> tuple[list[Row], list[tuple[str, str]]]:
    """The rows that can run, and the ones that cannot with their reason."""
    ft_python = os.environ.get("FT_PYTHON", sys.executable)
    ft_build = Path(os.environ["FT_BUILD_DIR"]) if "FT_BUILD_DIR" in os.environ \
        else latest_build_dir(ft_python)
    candidates = [Row("ft-gil-off", ft_python, ft_build, gil=False),
                  Row("ft-gil-on", ft_python, ft_build, gil=True)]

    gil_python = os.environ.get("GIL_PYTHON")
    gil_build = os.environ.get("GIL_BUILD_DIR")
    if gil_python and gil_build:
        candidates.insert(0, Row("classic", gil_python, Path(gil_build), gil=True))
    elif gil_python or gil_build:
        sys.exit("GIL_PYTHON and GIL_BUILD_DIR belong together; set both")
    else:
        # Named, not omitted: the row is part of the evidence, and a debug
        # build against a traditional interpreter is what it needs.
        return ([r for r in candidates if not check(r)],
                [("classic", "GIL_PYTHON and GIL_BUILD_DIR not set")]
                + [(r.name, why) for r in candidates if (why := check(r))])

    usable, missing = [], []
    for row in candidates:
        why = check(row)
        (missing.append((row.name, why)) if why else usable.append(row))
    return usable, missing


def env_for(row: Row) -> dict:
    env = dict(os.environ)
    env.update(
        BUILD_DIR=os.fspath(row.build),
        PYTHONPATH=os.fspath(package_dir(row.build)),
        PYSIDE_DISABLE_INTERNAL_QT_CONF="1",
        QT_NO_GLIB="1",
        PYTHON_GIL="1" if row.gil else "0",
        # The child verifies this after importing PySide, because that import
        # is what can turn the GIL back on. A row that silently ran in the
        # wrong mode would be a third measurement of the same thing.
        FAILPOINT_EXPECT_GIL="1" if row.gil else "0",
    )
    return env


def classify(rc: int) -> str:
    if rc == 0:
        return "ok"
    if rc == SKIP_RC:
        return "skip"
    if rc < 0:
        return f"CRASH({signal.Signals(-rc).name})"
    if rc == 124:
        return "HANG"
    if rc == 2:
        return "SETUP"
    return "FAIL"


def run_one(row: Row, test: str, expect: str) -> tuple[str, str]:
    # A test whose expected outcome is a deadlock gets a shorter leash: the
    # wait is the result, so there is nothing to gain from waiting the full
    # timeout for it.
    timeout = TIMEOUT if expect != "HANG" else min(TIMEOUT, 20)
    command = [row.python, os.fspath(WORKER), test]
    proc = subprocess.Popen(command, env=env_for(row), cwd=os.fspath(REPO),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        # The whole group: a deadlocked test leaves threads parked in a
        # mutex, and the process will not go on its own.
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        rc = 124
    return classify(rc), out


def test_names(row: Row) -> dict[str, str]:
    """The tests this build knows, and what each one has to produce."""
    out = subprocess.run([row.python, os.fspath(WORKER), "--list"],
                         env=env_for(row), cwd=os.fspath(REPO),
                         capture_output=True, text=True, timeout=TIMEOUT)
    if out.returncode != 0:
        sys.exit(f"cannot list the tests with {row.python}:\n{out.stdout}"
                 f"{out.stderr}")
    listed = {}
    for line in out.stdout.split():
        name, _, expect = line.partition(":")
        listed[name] = expect or "ok"
    return listed


def main() -> int:
    usable, missing = rows()
    if not usable:
        for name, why in missing:
            print(f"{name}: {why}", file=sys.stderr)
        return 2

    known = test_names(usable[0])
    wanted = sys.argv[1:] or list(known)
    unknown = [t for t in wanted if t not in known]
    if unknown:
        print(f"unknown test(s): {' '.join(unknown)}", file=sys.stderr)
        print(f"known: {' '.join(known)}", file=sys.stderr)
        return 2

    for row in usable:
        print(f"{row.name:<11} {row.python}")
        print(f"{'':<11} {row.build}")
    for name, why in missing:
        print(f"{name:<11} MISSING - {why}")
    print(f"timeout: {TIMEOUT}s per test")
    print()

    header = f"{'test':<22}" + "".join(f"{r.name:<14}" for r in usable)
    print(header)
    print("-" * len(header))

    results: dict[tuple[str, str], tuple[str, str]] = {}
    for test in wanted:
        expect = known[test]
        cells = []
        for row in usable:
            verdict, out = run_one(row, test, expect)
            results[(test, row.name)] = (verdict, out)
            # A cell that produced what it had to says so, rather than
            # printing HANG next to a test whose point is to hang.
            cells.append(verdict if verdict != expect or expect == "ok"
                         else f"{verdict}=ok")
        label = test if expect == "ok" else f"{test} [{expect}]"
        print(f"{label:<22}" + "".join(f"{c:<14}" for c in cells))

    bad = [(t, r) for (t, r), (v, _) in results.items()
           if v not in ("skip", known[t])]
    if bad:
        print()
        for test, row in bad:
            verdict, out = results[(test, row)]
            print(f"--- {test} on {row}: {verdict}")
            print(out.rstrip())
        print()
        print(f"FAILED: {len(bad)} of {len(results)} cells")
        return 1

    skipped = sorted({r for (_, r), (v, _) in results.items() if v == "skip"})
    print()
    if skipped:
        print("skipped (no failpoints in that build, or the test says the "
              "row cannot measure it): " + " ".join(skipped))
    if missing:
        print("PARTIAL: " + ", ".join(f"{n} ({w})" for n, w in missing))
        print("The validation plan asks for all three rows; this run is not "
              "that evidence yet.")
        return 3
    print(f"clean on all {len(usable)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
