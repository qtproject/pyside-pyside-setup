#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""
Free-threading A/B proof harness (PoC).

Runs every scenario twice against the SAME free-threaded binary, once with
the synchronization it needs and once without. Which one is switched off
depends on the scenario:

  * the wrapper lifecycle scenarios clear the state lock bit
  * lazy_types clears the lazy type creation bit

All of them go through PYSIDE6_OPTION_FT, the flags variable in
sbkftoptions.h; a run clears exactly the one bit its scenario is about.

Scenarios come in two kinds. A "proof" scenario has to crash with its lock
switched off - that is what shows it reaches the race at all; passing both
ways proves nothing, it may simply never collide. A "regression" scenario is
only required to stay clean; it is kept because it once broke, not because
it demonstrates anything.

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
from enum import IntFlag
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
WORKER = Path(__file__).resolve().parent / "stress.py"


def has_sample(build: Path) -> bool:
    """Whether this build can run the scenarios at all. Without --build-tests
    there is no sample module, and every scenario fails to import - a full run
    of failed starts, which reads like a result."""
    return bool(list(build.glob("shiboken6/tests/samplebinding/sample.*")))


def latest_build_dir() -> Path:
    """The newest build that has the sample binding."""
    history = REPO / "build_history"
    entries = sorted((p for p in history.glob("*/build_dir.txt")),
                     key=lambda p: p.parent.name, reverse=True)
    for entry in entries:
        build = Path(entry.read_text().splitlines()[0])
        if has_sample(build):
            return build
    sys.exit("No build with the sample binding found. Build with "
             f"--build-tests, or set BUILD_DIR. ({history})")


# The stress worker runs in a subprocess, so the interpreter has to be named
# explicitly; by default it is the one running this script.
PY = os.environ.get("STRESS_PYTHON", sys.executable)
QT_DIR = os.environ.get("QT_DIR")
BUILD = Path(os.environ["BUILD_DIR"]) if "BUILD_DIR" in os.environ \
    else latest_build_dir()
# Also when BUILD_DIR names it: the check is worth more there, because an
# explicit path is usually one that was right yesterday. A matrix build over
# the variants leaves this directory holding a subset build without tests.
if not has_sample(BUILD):
    sys.exit(f"No sample binding under {BUILD} - rebuild with --build-tests.")
PKG = BUILD.parent / "package_for_wheels"

REPEATS = int(os.environ.get("REPEATS", "10"))
TIMEOUT = int(os.environ.get("STRESS_TIMEOUT", "120"))


class Lock(IntFlag):
    """The bits of PYSIDE6_OPTION_FT, mirroring sbkftoptions.h.

    A scenario runs twice: once with ALL, once with its own bit cleared.
    """

    COARSE_BINDING = 0x1
    LAZY_TYPE = 0x2
    STATE = 0x4
    ALL = COARSE_BINDING | LAZY_TYPE | STATE


MODES = ["unlocked", "locked"]

# scenario -> (script to run, argument, the lock bit it clears, proof)
QQML_TEST = (REPO / "sources" / "pyside6" / "tests" / "QtQml"
             / "qqmlnetwork_test.py")
SCENARIOS = {
    "shared_delete": (WORKER, "shared_delete", Lock.STATE, True),
    "call_vs_delete": (WORKER, "call_vs_delete", Lock.STATE, True),
    # A wrapper enters Object::destroy() from the C++ destructor of its owner
    # while other threads are calling into it. Crashes in BOTH columns right
    # now: a lease covers Shiboken.delete() of its own object, not the
    # destruction of the object that owns it. Clean before the coarse guard
    # was taken out of the generated wrapper entry.
    "child_delete_vs_call": (WORKER, "child_delete_vs_call", Lock.STATE, True),
    # Signal connect/emit/disconnect: hand-written libpyside code, still
    # behind the coarse guard. Not marked as a proof - it stays clean in both
    # columns up to 12 threads and 6000 rounds, so it is a regression guard
    # over the signal machinery, not evidence for the lock.
    "signal_race": (WORKER, "signal_race", Lock.COARSE_BINDING, False),
    # Guards the map lookup against handing out a dying wrapper. Not marked
    # as a proof: what fixed it was acquireWrapper(), not the state lock, so
    # both modes are expected clean. Read its docstring before believing a
    # crash here - it can also die on a dangling C++ pointer, which says
    # nothing.
    "lookup_vs_last_decref": (WORKER, "lookup_vs_last_decref",
                              Lock.STATE, False),
    # Kept as a regression guard: it races destruction, but every thread owns
    # its objects, so nothing the state lock protects is contended and it
    # stays clean either way.
    "destroy_race": (WORKER, "destroy_race", Lock.STATE, False),
    # Qt calls the network access manager factory from its QML loader thread,
    # so this incarnates types there while the main thread incarnates others.
    "lazy_types": (QQML_TEST, None, Lock.LAZY_TYPE, True),
}
ALL_SCENARIOS = list(SCENARIOS)


def base_env(lock_bit: Lock, mode: str) -> dict:
    env = dict(os.environ)
    env.update(
        BUILD_DIR=os.fspath(BUILD),
        PYSIDE_DISABLE_INTERNAL_QT_CONF="1",
        QT_NO_GLIB="1",
        PYTHONPATH=os.fspath(PKG),
    )
    flags = Lock.ALL if mode == "locked" else Lock.ALL & ~lock_bit
    # Binary on purpose: the variable is read as flags, so it should look
    # like flags in a log. sbkftoptions.h understands 0b, 0x and plain
    # decimal, like PYSIDE6_OPTION_PYTHON_ENUM does.
    env["PYSIDE6_OPTION_FT"] = bin(int(flags))
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


def run_one(scenario: str, mode: str) -> str:
    script, argument, lock_bit, _proof = SCENARIOS[scenario]
    command = [PY, os.fspath(script)]
    if argument:
        command.append(argument)
    try:
        p = subprocess.run(
            command, env=base_env(lock_bit, mode), cwd=os.fspath(REPO),
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
    header = (f"{'scenario':<22}"
              + "".join(f"{m:<12}" for m in MODES) + "kind")
    print(header)
    print("-" * len(header))

    verdicts = {}
    for scenario in scenarios:
        cells = []
        for mode in MODES:
            results = [run_one(scenario, mode) for _ in range(REPEATS)]
            crashed = sum(1 for r in results if r.startswith("CRASH"))
            hung = sum(1 for r in results if r == "HANG")
            others = sum(1 for r in results if r not in ("ok",)
                         and not (r.startswith("CRASH") or r == "HANG"))
            verdicts[(scenario, mode)] = (crashed + hung, others, results)
            # A hang is not a crash. Both mean the lock was needed, but only
            # one of them says a pointer went bad, and reading "CRASH" for a
            # deadlock sends the next person hunting the wrong bug.
            parts = [f"{crashed}CRASH" if crashed else "",
                     f"{hung}HANG" if hung else "",
                     f"{others}err" if others else ""]
            tag = "+".join(p for p in parts if p) or "ok"
            cells.append(f"{tag}/{REPEATS}")
        kind = "proof" if SCENARIOS[scenario][3] else "regression"
        print(f"{scenario:<22}" + "".join(f"{c:<12}" for c in cells) + kind)

    # verdict
    print()
    dirty = [s for s in scenarios
             if verdicts[(s, "locked")][0] or verdicts[(s, "locked")][1]]
    silent = [s for s in scenarios
              if SCENARIOS[s][3] and verdicts[(s, "unlocked")][0] == 0]

    if dirty:
        print("FAILED: not clean with the lock -> " + " ".join(dirty))
        return 2
    if silent:
        print("INCONCLUSIVE: these proof scenarios stay clean without their "
              "lock, so they show nothing -> " + " ".join(silent))
        print("Raise STRESS_ITERS/STRESS_THREADS/REPEATS, or the scenario "
              "does not actually share what the lock protects.")
        return 1
    proofs = [s for s in scenarios if SCENARIOS[s][3]]
    print(f"PROVEN ({len(proofs)}): crashes without the lock, clean with it -> "
          + " ".join(proofs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
