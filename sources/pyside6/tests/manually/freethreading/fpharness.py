#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""What the failpoint tests need in order to be tests.

Everything here is machinery: finding the build, arming a point, running
threads and collecting what went wrong, the QML fixtures, and the switch that
takes one measure away so a test can show the failure coming back.

The tests themselves are in failpoints.py, and what each of them is about is
in README.md next to it.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import sysconfig
import threading
from pathlib import Path
from typing import Callable, NamedTuple

import ftoptions

REPO = Path(__file__).resolve().parents[5]
SELF = Path(__file__).resolve().parent / "failpoints.py"

SKIP = 77           # no failpoints here; the matrix runner shows it as "skip"


def build_dir() -> Path:
    if "BUILD_DIR" in os.environ:
        return Path(os.environ["BUILD_DIR"])
    history = REPO / "build_history"
    entries = sorted(history.glob("*/build_dir.txt"), key=lambda p: p.parent.name,
                     reverse=True)
    for entry in entries:
        build = Path(entry.read_text().splitlines()[0])
        if build.is_dir():
            return build
    sys.exit("no build found; set BUILD_DIR")


BUILD = build_dir()
sys.path.insert(0, os.fspath(BUILD.parent / "package_for_wheels"))
# The shiboken test bindings, where the build has them. Only module init adds
# edges to the class graph, and a Core subset - which is what the sanitizer
# trees are - has no second PySide6 module to import; these are the modules
# that let the hierarchy test race anything at all.
for _binding in ("samplebinding", "otherbinding", "minimalbinding",
                 "smartbinding"):
    _path = BUILD / "shiboken6" / "tests" / _binding
    if _path.is_dir():
        sys.path.append(os.fspath(_path))

from shiboken6 import Shiboken  # noqa: E402
from PySide6.QtCore import QObject, QUrl  # noqa: E402

# Whether this interpreter has no GIL at all. PYTHON_GIL=1 turns the GIL back
# on for a run, but the build still has leases and critical sections, so this
# is a question about the build and not about the run.
FREE_THREADED = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def gil_enabled() -> bool:
    """Whether this interpreter runs with the GIL. A build older than 3.13
    has no such question and always does."""
    return sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True


def qt_app():
    """The application these tests need; event delivery and QML want one."""
    from PySide6.QtCore import QCoreApplication
    return QCoreApplication.instance() or QCoreApplication([])


def run_threads(targets, count: int = 1, timeout: float = 30.0) -> list[str]:
    """Run work on threads and report what went wrong, if anything.

    `targets` is one callable, run on `count` threads, or a list of different
    ones run on one thread each. Every test here needs the same four steps -
    start, join with a deadline, notice a thread that never came back, and
    keep the exception a worker raised, because a traceback printed from a
    thread does not fail a test.
    """
    errors: list[str] = []
    funcs = list(targets) if isinstance(targets, (list, tuple)) \
        else [targets] * count

    def wrapped(func: Callable[[], None]) -> None:
        try:
            func()
        except BaseException as exc:                # noqa: BLE001
            errors.append(repr(exc))

    threads = [threading.Thread(target=wrapped, args=(f,)) for f in funcs]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=timeout)
    if any(thread.is_alive() for thread in threads):
        errors.append("a thread did not come back")
    return errors


class FailpointMissing(Exception):
    """This build has no such point. Not a failure: the free-threading
    windows do not exist in a build with a GIL, and a release build has no
    failpoints at all. The test says so and the row shows a skip."""


class Failpoint:
    """Arm a point, let a thread run into it, release it afterwards."""

    def __init__(self, name: str, timeout_ms: int = 5000):
        self.name = name
        self.timeout_ms = timeout_ms

    def __enter__(self):
        if not Shiboken.armFailpoint(self.name, self.timeout_ms):
            raise FailpointMissing(self.name)
        return self

    def __exit__(self, *exc):
        Shiboken.releaseFailpoint(self.name)
        Shiboken.clearFailpoints()
        return False

    def wait_until_reached(self, timeout: float = 5.0) -> bool:
        """Whether a thread arrived. Polls rather than sleeping blindly: the
        test is about ordering, so it must not continue before the other
        thread is actually parked."""
        deadline = threading.Event()
        timer = threading.Timer(timeout, deadline.set)
        timer.start()
        try:
            while not deadline.is_set():
                if Shiboken.failpointReached(self.name):
                    return True
            return False
        finally:
            timer.cancel()

    def release(self) -> bool:
        return Shiboken.releaseFailpoint(self.name)


# --------------------------------------------------------------- QML fixtures

QML_IMPORT_NAME = "FailpointTest"
QML_IMPORT_MAJOR_VERSION = 1

# Set by the test that needs two threads inside construction at once; the
# registered type below waits on it. See README.md, "qml-placement-parallel".
parallel_barrier: threading.Barrier | None = None

# What the nested construction produced, so the nesting test can see it ran.
inner_names: list[str] = []

try:
    from PySide6.QtQml import QmlElement, QQmlComponent, QQmlEngine

    @QmlElement
    class Placed(QObject):
        """Creates another QObject before its own construction finishes."""

        def __init__(self, parent=None):
            inner = QObject()
            inner.setObjectName("inner")
            inner_names.append(inner.objectName())
            super().__init__(parent)
            self.setObjectName("placed")

    @QmlElement
    class Failing(QObject):
        """Ends in a Python error, after the generated constructor ran."""

        def __init__(self, parent=None):
            super().__init__(parent)
            raise RuntimeError("deliberate")

    @QmlElement
    class Parallel(QObject):
        """Will not finish constructing until a second thread is inside its
        own construction."""

        def __init__(self, parent=None):
            if parallel_barrier is not None:
                parallel_barrier.wait()
            super().__init__(parent)
            self.setObjectName("parallel")

    QML_READY = True
except ImportError:
    QML_READY = False


def qml_engine():
    """An engine, and the application it needs."""
    qt_app()
    return QQmlEngine()


def qml_create(engine, element: str):
    """Construct one QML element through a component, and hand back the
    object and the engine's opinion of it.

    Through the engine, not by calling the Python type: the placement address
    exists only inside createInto(), which a direct construction never
    reaches. A test that builds these types from Python exercises an ordinary
    constructor and says nothing about the placement at all.
    """
    component = QQmlComponent(engine)
    component.setData(f"import QtQml\nimport FailpointTest 1.0\n{element}"
                      .encode(), QUrl())
    if component.status() != QQmlComponent.Status.Ready:
        return None, component.errorString()
    return component.create(), component.errorString()


# ------------------------------------------------------------ counterproofs

# The measures a run can take away, read out of sbkftoptions.h rather than
# copied. The copy that used to stand here went stale and cleared a measure
# no counterproof had asked for.
OPTIONS = ftoptions.option_bits()
ALL_OPTIONS = ftoptions.all_bits(OPTIONS)


# How long a counterproof waits for its child. Deliberately a fraction of the
# matrix runner's own per-test budget: a counterproof whose subject is meant
# to hang would otherwise outlast the cell that started it, and the matrix
# would report the *counterproof* as a hang - which is the one thing it must
# not say, because that cell is green when the subject hangs. A hang is a
# hang after twenty seconds as well as after a hundred.
CHILD_TIMEOUT = max(20, int(os.environ.get("FAILPOINT_TIMEOUT", "60")) // 3)


def _run_without(cleared: list[str], test: str) -> tuple[int, str]:
    """Run one test in its own process with those measures switched off."""
    bits = ALL_OPTIONS
    for name in cleared:
        bits &= ~OPTIONS[name]
    env = dict(os.environ, PYSIDE6_OPTION_FT=hex(bits))
    env.pop("FAILPOINT_EXPECT_GIL", None)
    proc = subprocess.Popen([sys.executable, os.fspath(SELF), test], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=CHILD_TIMEOUT)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        rc = 124
    return rc, out


def counterproof(option: str, test: str) -> str:
    """Assert that test fails once option is taken away.

    This is what separates a test from a habit: one that passes with and
    without the measure it is named after demonstrates nothing, and running
    it both ways is the only way to find out which of the two it is.

    The run gets its own process, because the point of it is that it fails -
    by crashing, or by not coming back at all - and neither may take this
    one with it. The group is killed on a timeout, as the matrix runner
    kills its own children.
    """
    if not FREE_THREADED:
        return "skipped: the option bits exist only in a free-threaded build"
    rc, out = _run_without([option], test)
    # A subject that skipped is not a subject that failed. main() answers
    # SKIP for "nothing here ran", and SKIP is non-zero: read as a failure it
    # turns this row green in exactly the builds where it demonstrates
    # nothing - a release build with no failpoints, a tree without the sample
    # binding, a tree without QtQml.
    if rc == SKIP:
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        return f"skipped: {test} did not run ({tail[:60]})"
    if rc == 0:
        return (f"FAIL: {test} still passes without {option}, so it does not "
                f"test it")
    how = ("crashed" if rc < 0 else "hung" if rc == 124 else f"failed (rc {rc})")
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    return f"ok ({test} {how} without {option}: {tail[:60]})"


# ------------------------------------------------------------------- driver

class Test(NamedTuple):
    run: Callable[[], str]
    # What the matrix runner has to see. Not always "ok": the native-lock
    # boundary is a deadlock this project accepts and documents, so the test
    # for it states that, and a run in which it comes back is the failure.
    expect: str = "ok"


def main(tests: dict[str, Test]) -> int:
    if "--list" in sys.argv[1:]:
        for name, test in tests.items():
            print(f"{name}:{test.expect}")
        return 0

    # Asked after PySide is imported, not before: an extension without the
    # Py_mod_gil slot turns the GIL back on, and a row that ran in the wrong
    # mode would be a second measurement of the first one.
    expected = os.environ.get("FAILPOINT_EXPECT_GIL")
    if expected is not None and gil_enabled() != (expected == "1"):
        print(f"FAIL: asked for the GIL {'on' if expected == '1' else 'off'}, "
              f"this process has it {'on' if gil_enabled() else 'off'}")
        return 2

    print(f"build : {BUILD}")
    print(f"points: {Shiboken.failpointNames() or '(none in this build)'}")
    print(f"GIL   : {'on' if gil_enabled() else 'off'}")
    print()

    wanted = sys.argv[1:] or list(tests)
    failed = skipped = 0
    for name in wanted:
        if name not in tests:
            print(f"unknown test {name!r}; known: {' '.join(tests)}")
            return 2
        Shiboken.clearFailpoints()
        try:
            outcome = tests[name].run()
        except FailpointMissing as missing:
            outcome = f"skipped: this build has no failpoint {missing!s}"
        except Exception as exc:              # noqa: BLE001
            outcome = f"FAIL: raised {exc!r}"
        print(f"{name:24} {outcome}")
        failed += outcome.startswith("FAIL")
        skipped += outcome.startswith("skipped")
    print()
    print("all clean" if not failed else f"{failed} failed")
    if failed:
        return 1
    # Every test skipped means this run says nothing about the build, and the
    # matrix has to show that rather than a green cell.
    return SKIP if skipped == len(wanted) else 0
