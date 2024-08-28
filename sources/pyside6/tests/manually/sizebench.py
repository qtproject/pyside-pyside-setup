# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
"""
sizebench.py

Benchmark the size reduction of QtCore, QtGui and QtWidgets binaries.

The project will be built twice in release mode (unchecked)
 - with option "--unoptimize=all"
 - without any option.

Then values and relative improvement are printed.

No argument: Use a default Python for each platform (author specific).

    --python <python>   use that specific python interpreter
    --dry-run           try it first without compilation
    --pip               automatically install the needed modules
"""
import argparse
import os
import platform
import re
import subprocess
import sys

from ast import literal_eval
from pathlib import Path

defaults = {
    "Darwin": "/Users/tismer/.pyenv/versions/3.12.5/bin/python3",
    "Windows": "d:/py312_64/python.exe",
    "Linux": "/home/ctismer/.pyenv/versions/3.12.5/bin/python3",
}


def setup_project_dir():
    look_for = Path("testing")
    here = Path(__file__).resolve().parent
    while here / look_for not in here.iterdir():
        parent = here.parent
        if parent == here:
            raise SystemError(look_for + " not found!")
        here = parent
    fsp = os.fspath(here)
    if fsp not in sys.path:
        sys.path.insert(0, fsp)


def get_build_dir():
    from testing.buildlog import builds
    if not builds.history:
        raise
    return builds.history[-1].build_dir


def check_allowed_python_versions(major, minor):
    from build_scripts.main import config
    pattern = r'Programming Language :: Python :: (\d+)\.(\d+)'
    hist = []
    for line in config.python_version_classifiers:
        found = re.search(pattern, line)
        if found:
            ma = int(found.group(1))
            mi = int(found.group(2))
            if major == ma and minor == mi:
                return True
            hist.append((ma, mi))
    raise ValueError(hist)


def get_result_size(build_dir):
    result_dir = Path(build_dir) / "pyside6" / "PySide6"
    sum = 0
    awaited = 3
    got = 0
    with os.scandir(result_dir) as it:
        for entry in it:
            name = entry.name
            if (name.startswith(("QtCore.", "QtGui.", "QtWidgets."))
                    and name.endswith((".so", ".pyd"))):
                size = entry.stat().st_size
                print(f"{name=} {size=}")
                sum += size
                got += 1
    if awaited != got:
        raise ValueError(f"got {got} values, expected {awaited}")
    return sum


setup_project_dir()
plat = platform.system()
options = [
    "setup.py", "build", "--limited-api=no", "--skip-docs", "--no-qt-tools",
    "--module-subset=Core,Gui,Widgets"]

options_base = options + ["--unoptimize=all"]
options_best = options

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", "-p", nargs="?")
    parser.add_argument("--dry-run", "-d", action="store_true")
    parser.add_argument("--pip", action="store_true", help="""
        Install the necessary modules automatically, which can save some trouble""")
    args = parser.parse_args()

    python = args.python or defaults[plat] if plat in defaults else args.python
    python = Path(python).expanduser()

    if not python.exists:
        raise ValueError(f"Python executable `{python}` not found")
    version = subprocess.check_output([python, "-c", "import sys; print(sys.version_info[:2])"])
    major, minor = literal_eval(version.decode())
    try:
        check_allowed_python_versions(major, minor)
    except ValueError as e:
        msg = " ".join(f"{ma}.{mi}" for (ma, mi) in e.args[0])
        raise ValueError(f"Python versions allowed = {msg}, got {major}.{minor}") from None

    needs_imports = ["packaging", "setuptools"]
    if args.pip:
        # This way, setuptools seems to install reliably.
        subprocess.run([python, "-m", "pip", "install"] + needs_imports)
        subprocess.run([python, "-m", "pip", "uninstall", "-y"] + needs_imports)
        subprocess.run([python, "-m", "pip", "install"] + needs_imports)

    skip = args.dry_run
    cmd = [python] + options_base
    if not skip:
        subprocess.run(cmd)

    build_dir = get_build_dir()
    res_base = get_result_size(build_dir)

    cmd = [python] + options_best
    if not skip:
        subprocess.run(cmd)

    build_dir = get_build_dir()
    res_best = get_result_size(build_dir)

    print()
    print(f"Compiling with {python}")
    print(f"Platform = {plat}")
    print(f"base size = {res_base}")
    print(f"best size = {res_best}")
    print(f"improvement {(res_base - res_best) / res_base:%}")
    if skip:
        raise ValueError("This result is only fake. Please run it again without the "
                         "--dry-run argument")
