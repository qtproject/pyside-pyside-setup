#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""
Free-threading A/B proof harness (PoC).

Runs every scenario twice against the SAME free-threaded binary, once with
the synchronization it needs and once without. Which one is switched off
depends on the scenario:

  * the object graph scenarios toggle the CoarseBindingGuard (PYSIDE_COARSE_BINDING_LOCK)
  * lazy_types toggles the lazy type creation lock (PYSIDE_LAZY_LOCK)

Each scenario is launched as a fresh subprocess REPEATS times. A subprocess
that dies from a signal (SIGSEGV/SIGABRT -> negative return code) is a real
C++ data race. The proof we want:

    unlocked -> crashes    AND    locked -> clean

This is deliberately not part of the automatic test suite: half of the proof
consists of processes that die from SIGSEGV.

Run it with the free-threaded interpreter you want to test; it uses the most
recent build with the sample binding unless BUILD_DIR says otherwise. Name
scenarios as arguments to run only those. STRESS_PYTHON, QT_DIR, REPEATS,
STRESS_TIMEOUT, STRESS_THREADS and STRESS_ITERS override the defaults:

    run.py                                  all scenarios, 10 repeats
    REPEATS=50 STRESS_ITERS=20000 run.py shared_delete
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
WORKER = Path(__file__).resolve().parent / "stress.py"


def latest_build_dir() -> Path:
    """The newest build that has the sample binding.

    The newest build as such is not enough: a build made without
    --build-tests has no sample module, and every scenario would fail with an
    import error instead of proving anything.
    """
    history = REPO / "build_history"
    entries = sorted((p for p in history.glob("*/build_dir.txt")),
                     key=lambda p: p.parent.name, reverse=True)
    for entry in entries:
        build = Path(entry.read_text().splitlines()[0])
        if list(build.glob("shiboken6/tests/samplebinding/sample.*")):
            return build
    sys.exit("No build with the sample binding found. Build with "
             f"--build-tests, or set BUILD_DIR. ({history})")


# The stress worker runs in a subprocess, so the interpreter has to be named
# explicitly; by default it is the one running this script.
PY = os.environ.get("STRESS_PYTHON", sys.executable)
QT_DIR = os.environ.get("QT_DIR")
BUILD = Path(os.environ["BUILD_DIR"]) if "BUILD_DIR" in os.environ \
    else latest_build_dir()
PKG = BUILD.parent / "package_for_wheels"

REPEATS = int(os.environ.get("REPEATS", "10"))
TIMEOUT = int(os.environ.get("STRESS_TIMEOUT", "120"))
MODES = [("unlocked", "0"), ("locked", "1")]

# scenario -> (script to run, argument, environment switch it toggles)
QQML_TEST = (REPO / "sources" / "pyside6" / "tests" / "QtQml"
             / "qqmlnetwork_test.py")
SCENARIOS = {
    "shared_parent": (WORKER, "shared_parent", "PYSIDE_COARSE_BINDING_LOCK"),
    "destroy_race": (WORKER, "destroy_race", "PYSIDE_COARSE_BINDING_LOCK"),
    "reparent": (WORKER, "reparent", "PYSIDE_COARSE_BINDING_LOCK"),
    "shared_delete": (WORKER, "shared_delete", "PYSIDE_COARSE_BINDING_LOCK"),
    # Qt calls the network access manager factory from its QML loader thread,
    # so this incarnates types there while the main thread incarnates others.
    "lazy_types": (QQML_TEST, None, "PYSIDE_LAZY_LOCK"),
}
ALL_SCENARIOS = list(SCENARIOS)


def base_env(switch: str, value: str) -> dict:
    env = dict(os.environ)
    env.update(
        BUILD_DIR=os.fspath(BUILD),
        PYSIDE_DISABLE_INTERNAL_QT_CONF="1",
        QT_NO_GLIB="1",
        PYTHONPATH=os.fspath(PKG),
    )
    env[switch] = value
    if QT_DIR:
        env["QT_DIR"] = QT_DIR
    return env


def classify(rc: int) -> str:
    if rc == 0:
        return "ok"
    if rc < 0:
        return f"CRASH({signal.Signals(-rc).name})"
    if rc == 3:
        return "pyerr"
    if rc == 124:
        return "HANG"
    return f"exit{rc}"


def run_one(scenario: str, value: str) -> str:
    script, argument, switch = SCENARIOS[scenario]
    command = [PY, os.fspath(script)]
    if argument:
        command.append(argument)
    try:
        p = subprocess.run(
            command, env=base_env(switch, value), cwd=os.fspath(REPO),
            capture_output=True, timeout=TIMEOUT)
        return classify(p.returncode)
    except subprocess.TimeoutExpired:
        return "HANG"


def main() -> int:
    scenarios = sys.argv[1:] or ALL_SCENARIOS
    unknown = [s for s in scenarios if s not in ALL_SCENARIOS]
    if unknown:
        print(f"unknown scenario(s): {' '.join(unknown)}", file=sys.stderr)
        print(f"usage: run.py [{' | '.join(ALL_SCENARIOS)}]", file=sys.stderr)
        return 2

    print(f"python : {PY}")
    print(f"build  : {BUILD}")
    print(f"repeats: {REPEATS}  timeout: {TIMEOUT}s  "
          f"threads: {os.environ.get('STRESS_THREADS', '8')}  "
          f"iters: {os.environ.get('STRESS_ITERS', '6000')}")
    print()
    header = f"{'scenario':<16}" + "".join(f"{m:<12}" for m, _ in MODES)
    print(header)
    print("-" * len(header))

    verdicts = {}
    for scenario in scenarios:
        cells = []
        for mode, own in MODES:
            results = [run_one(scenario, own) for _ in range(REPEATS)]
            crashes = sum(1 for r in results if r.startswith("CRASH")
                          or r == "HANG")
            others = sum(1 for r in results if r not in ("ok",)
                         and not (r.startswith("CRASH") or r == "HANG"))
            verdicts[(scenario, mode)] = (crashes, others, results)
            tag = "ok" if crashes == 0 and others == 0 else \
                  f"{crashes}CRASH" if crashes else f"{others}err"
            cells.append(f"{tag}/{REPEATS}")
        print(f"{scenario:<16}" + "".join(f"{c:<12}" for c in cells))

    # verdict
    print()
    unlocked = sum(verdicts[(s, "unlocked")][0] for s in scenarios)
    locked = sum(verdicts[(s, "locked")][0] for s in scenarios)
    print(f"unlocked crashes+hangs: {unlocked}")
    print(f"locked   crashes+hangs: {locked}")
    if unlocked > 0 and locked == 0:
        print("\nPROVEN: these paths race without their lock and are stable "
              "with it.")
        return 0
    if unlocked == 0:
        print("\nINCONCLUSIVE: nothing crashed unlocked -> stress not "
              "aggressive enough, or the interpreter already covers this. "
              "Raise STRESS_ITERS/STRESS_THREADS/REPEATS.")
        return 1
    print("\nFAILED: still crashes with the lock -> coverage incomplete.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
