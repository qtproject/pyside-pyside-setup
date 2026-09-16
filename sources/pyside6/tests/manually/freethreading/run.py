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
from typing import NamedTuple

import ftoptions

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
WORKER = HERE.parent / "stress.py"
METAOBJECT = HERE.parent / "metaobject_lock.py"
POST_ROUTINE = HERE.parent / "post_routine_batch.py"
POST_RAISES = HERE.parent / "post_routine_raises.py"
RECEIVER = HERE.parent / "method_receiver_dead.py"


def has_sample(build: Path) -> bool:
    """Whether this build can run the scenarios at all. Without --build-tests
    there is no sample module, and every scenario fails to import - a full run
    of failed starts, which reads like a result."""
    return bool(list(build.glob("shiboken6/tests/samplebinding/sample.*")))


def built_lib(build: Path, where: str, name: str) -> Path | None:
    """One built library, which is what the tree is asked about below."""
    directory = build / where
    libs = sorted(directory.glob(f"{name}*.dylib")) \
        + sorted(directory.glob(f"{name}*.so"))
    return libs[0] if libs else None


def undefined_symbols(lib: Path) -> str:
    """What the library calls and does not define. Raises when nm does not
    answer: an empty result is indistinguishable from a clean one, and both
    callers below read a blank as the absence of what they look for."""
    nm = subprocess.run(["nm", "-u", os.fspath(lib)],
                        capture_output=True, text=True)
    if nm.returncode != 0:
        sys.exit(f"nm failed on {lib}: {nm.stderr.strip()}")
    return nm.stdout


def tree_sanitizer(build: Path) -> str:
    """Which sanitizer the tree was built with, asked of the tree itself."""
    lib = built_lib(build, "shiboken6/libshiboken", "libshiboken6")
    if lib is None:
        return "none"
    undefined = undefined_symbols(lib)
    return next((t for t in ("tsan", "asan") if t in undefined), "none")


def contract_checked(build: Path) -> bool:
    """Whether the lock contract assertions are compiled in, asked of the
    tree itself. Under NDEBUG checkNoRawLock() is an inline no-op, so a
    scenario that proves itself by tripping it stays clean in both columns
    - a skip that reads like a pass.

    libpyside is the one to ask, not libshiboken: the assertion the
    meta-object scenario trips sits in parsePythonType(), and whether that
    call survived the preprocessor is libpyside's NDEBUG, not the one the
    function was declared under. A call that is there shows up as an
    undefined symbol."""
    lib = built_lib(build, "pyside6/libpyside", "libpyside6")
    if lib is None:
        return False
    return "checkNoRawLock" in undefined_symbols(lib)


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
# A sanitizer-built tree cannot be measured here. It kills the process at its
# first report - abort_on_error is 1 on Darwin - so every scenario the tool
# has anything to say about reads as a crash in both columns. Turning that
# off is worse: with exitcode=0 a real SIGSEGV exits 0, and dynamic_property,
# which segfaults, reported ok/10. A sanitizer run is a different question
# and wants a runner that counts reports.
built_with = tree_sanitizer(BUILD)
if built_with != "none":
    sys.exit(f"{BUILD} is built with {built_with}. This harness counts "
             "crashes and cannot tell a sanitizer's abort from one.")
PKG = BUILD.parent / "package_for_wheels"
CONTRACT = contract_checked(BUILD)

REPEATS = int(os.environ.get("REPEATS", "10"))
TIMEOUT = int(os.environ.get("STRESS_TIMEOUT", "120"))


BITS = ftoptions.option_bits()
Lock = IntFlag("Lock", BITS)

MODES = ["unlocked", "locked"]


class Scenario(NamedTuple):
    script: Path
    argument: str | None
    lock: Lock          # the bit its A/B clears
    proof: bool         # must crash without that bit, or it shows nothing
    needs_contract: bool = False   # nothing to say without the assertions


QQML_TEST = (REPO / "sources" / "pyside6" / "tests" / "QtQml"
             / "qqmlnetwork_test.py")
SCENARIOS = {
    "shared_delete": Scenario(WORKER, "shared_delete", Lock.StateLock, True),
    "call_vs_delete": Scenario(WORKER, "call_vs_delete", Lock.StateLock, True),
    # A wrapper enters Object::destroy() from the C++ destructor of its owner
    # while other threads are calling into it. This is what the lease has to
    # cover transitively: not the object being deleted, but everything that
    # deletion takes with it.
    "child_delete_vs_call": Scenario(WORKER, "child_delete_vs_call", Lock.StateLock, True),
    # Signal connect/emit/disconnect in hand-written libpyside code. It was a
    # regression guard while the coarse lock covered these paths, and became a
    # proof when that lock went: the signal machinery reaches the wrapper
    # lookups, the parent/child graph and destruction, and those are the state
    # lock's. 15 crashes out of 15 without it, clean with it.
    "signal_race": Scenario(WORKER, "signal_race", Lock.StateLock, True),
    # Guards the map lookup against handing out a dying wrapper. Not marked
    # as a proof: what fixed it was acquireWrapper(), not the state lock, so
    # both modes are expected clean. Read its docstring before believing a
    # crash here - it can also die on a dangling C++ pointer, which says
    # nothing.
    "lookup_vs_last_decref": Scenario(WORKER, "lookup_vs_last_decref",
                                      Lock.StateLock, False),
    # Kept as a regression guard: it races destruction, but every thread owns
    # its objects, so nothing the state lock protects is contended and it
    # stays clean either way.
    "destroy_race": Scenario(WORKER, "destroy_race", Lock.StateLock, False),
    # The one-time incarnation of a type, raced by every thread at once.
    # Cheaper and far more reliable than lazy_types, and it needs no QML.
    # The call guard has to come out with it: it serializes calls on one
    # object as a side effect, which hides this race and made the scenario
    # inconclusive once CallGuard entered ALL. What is proven is still the
    # lazy lock - the guard is only kept out of the way.
    "lazy_converter": Scenario(WORKER, "lazy_converter",
                               Lock.LazyTypeLock | Lock.CallGuard, True),
    # Qt calls the network access manager factory from its QML loader thread,
    # so this incarnates types there while the main thread incarnates others.
    "lazy_types": Scenario(QQML_TEST, None, Lock.LazyTypeLock, True),
    # Every thread inside one C++ object at once - what the GIL used to
    # prevent by accident and the per-object call guard now does on purpose.
    "shared_setter": Scenario(WORKER, "shared_setter", Lock.CallGuard, True),
    # The five below come from what applications do rather than from a code
    # path we wanted to prove. Two of them earned a proof mark on 04.09.,
    # each lock switched off on its own, five rounds per column:
    #
    #                      all on  no lazy  no state  no guard  all off
    #   move_to_thread       0/5      0/5      5/5       0/5      5/5
    #   container_convert    0/5      5/5      0/5       0/5      5/5
    #
    # container_convert was entered under Lock.StateLock by assumption; the
    # measurement says the lazy type lock is what carries it.
    "queued_signal": Scenario(WORKER, "queued_signal", Lock.StateLock, False),
    # An object handed to another thread while the first one still uses it.
    "move_to_thread": Scenario(WORKER, "move_to_thread", Lock.StateLock, True),
    # Converting a container incarnates the element type on first use.
    "container_convert": Scenario(WORKER, "container_convert",
                                  Lock.LazyTypeLock, True),
    # Not a proof: the threads that lose the race write the same offsets, so
    # nothing crashes either way. It is here so a sanitizer run has the two
    # sides to compare - see the scenario's docstring in stress.py.
    "mi_first_instance": Scenario(WORKER, "mi_first_instance",
                                  Lock.MiOffsetsOnce, False),
    # No proof mark, and it never will be one: this crashes with the GIL as
    # well and on a released wheel. It is an ordinary PySide bug that the
    # scenario happens to hit, and it takes three lines to reproduce.
    # Kept so the crash stays visible until it is fixed.
    "dynamic_property": Scenario(WORKER, "dynamic_property", Lock.StateLock, False),
    "virtual_override": Scenario(WORKER, "virtual_override", Lock.StateLock, False),
    # The odd one out: one thread, one subprocess, no timing window, so a
    # single repeat says as much as fifty. Adding a dynamic signal parses the
    # Python type, and the contract assertion at the top of parsePythonType()
    # aborts when the parse is put back under the meta-object lock. It needs
    # a debug build - under NDEBUG the assertion is empty and both columns
    # read ok, which is a skip wearing a pass.
    "metaobject_lock": Scenario(METAOBJECT, None,
                                Lock.MetaObjectParseOutsideLock, True,
                                needs_contract=True),
    # B16-2. Debug build only, like metaobject_lock.
    # See README.
    "post_routine_batch": Scenario(POST_ROUTINE, None,
                                   Lock.PostRoutineBatch, True,
                                   needs_contract=True),
    # B16-2, the pending exception. Debug build only.
    # See README.
    "post_routine_raises": Scenario(POST_RAISES, None,
                                    Lock.PostRoutineBatch, True,
                                    needs_contract=True),
    # B12-4/B14-4, a delivery to a dead receiver.
    # See README.
    "method_receiver_dead": Scenario(RECEIVER, None,
                                     Lock.MethodReceiverUpgrade, True),
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
    if mode == "locked":
        # Left unset, which sbkftoptions.h reads as every bit there is -
        # including one this file has never heard of. A number here would be
        # a second copy of the inventory, and the second copy is the one that
        # goes stale.
        env.pop("PYSIDE6_OPTION_FT", None)
    else:
        # All of them except this one, see sbkftoptions.h.
        env["PYSIDE6_OPTION_FT"] = f"~{lock_bit:#x}"
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
    sc = SCENARIOS[scenario]
    command = [PY, os.fspath(sc.script)]
    if sc.argument:
        command.append(sc.argument)
    try:
        p = subprocess.run(
            command, env=base_env(sc.lock, mode), cwd=os.fspath(REPO),
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

    # Before the table, not after it: a scenario this build cannot answer
    # would otherwise be launched 2 x REPEATS times to have its result
    # thrown away.
    skipped = [] if CONTRACT else [s for s in scenarios
                                   if SCENARIOS[s].needs_contract]
    scenarios = [s for s in scenarios if s not in skipped]

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
        kind = "proof" if SCENARIOS[scenario].proof else "regression"
        print(f"{scenario:<22}" + "".join(f"{c:<12}" for c in cells) + kind)

    # verdict
    print()
    dirty = [s for s in scenarios
             if verdicts[(s, "locked")][0] or verdicts[(s, "locked")][1]]
    # An error counts as evidence like a crash or a hang: what a debug build
    # reports as a failing assertion, a release interpreter reports as the
    # scenario's own error message. Only a run that shows nothing at all
    # proves nothing. Found on 3.14t, where method_receiver_dead answered
    # 60err/60 unlocked against ok/60 locked and was called inconclusive.
    silent = [s for s in scenarios
              if SCENARIOS[s].proof
              and verdicts[(s, "unlocked")][0] == 0
              and verdicts[(s, "unlocked")][1] == 0]

    if dirty:
        print("FAILED: not clean with the lock -> " + " ".join(dirty))
        return 2
    if silent:
        print("INCONCLUSIVE: these proof scenarios stay clean without their "
              "lock, so they show nothing -> " + " ".join(silent))
        print("Raise STRESS_ITERS/STRESS_THREADS/REPEATS, or the scenario "
              "does not actually share what the lock protects.")
        return 1
    if skipped:
        print("SKIPPED: no contract assertions in this build, so these prove "
              "nothing here -> " + " ".join(skipped))
        print("Build with --debug to run them.")
    proofs = [s for s in scenarios if SCENARIOS[s].proof]
    print(f"PROVEN ({len(proofs)}): crashes without the lock, clean with it -> "
          + " ".join(proofs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
