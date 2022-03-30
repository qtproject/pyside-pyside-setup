#############################################################################
##
## Copyright (C) 2019 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
This script is used by Coin (coin_test_instructions.py specifically) to
test installation of generated wheels, and test building of the
"buildable" examples samplebinding and scriptableapplication.

It can also be invoked regularly from the command line via
python testing/wheel_tester.py --qmake=some-value --cmake=some-value

The qmake and cmake arguments can also be omitted, and they will be
looked up in your PATH.

Make sure that some generated wheels already exist in the dist/
directory (e.g. setup.py bdist_wheel was already executed).
"""

import os
import platform
import sys
import tempfile
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
this_dir = os.path.dirname(this_file)
setup_script_dir = os.path.abspath(os.path.join(this_dir, ".."))
sys.path.append(setup_script_dir)

from setuptools._distutils import log

from build_scripts.utils import (find_files_using_glob, find_glob_in_path,
                                 rmtree, run_process, run_process_output)

log.set_verbosity(1)

NEW_WHEELS = False


def find_executable(executable, command_line_value):
    value = command_line_value
    option_str = f"--{executable}"

    if value:
        log.info(f"{option_str} option given: {value}")
        if not os.path.exists(value):
            raise RuntimeError(f"No executable exists at: {value}")
    else:
        log.info(f"No {option_str} option given, trying to find {executable} in PATH.")
        paths = find_glob_in_path(executable)
        log.info(f"{executable} executables found in PATH: {paths}")
        if not paths:
            raise RuntimeError(
                f"No {option_str} option was specified and no {executable} was " "found in PATH."
            )
        else:
            value = paths[0]
            log.info(f"Using {executable} found in PATH: {value}")
    log.info("")
    return value


QMAKE_PATH = None
CMAKE_PATH = None


def get_wheels_dir(dir_name):
    return os.path.join(setup_script_dir, dir_name)


def get_examples_dir():
    return os.path.join(setup_script_dir, "examples")


def package_prefix_names():
    # Note: shiboken6_generator is not needed for compile_using_nuitka,
    # but building modules with cmake needs it.
    if NEW_WHEELS:
        return ["shiboken6", "shiboken6_generator", "PySide6_Essentials", "PySide6_Addons", "PySide6"]
    else:
        return ["shiboken6", "shiboken6_generator", "PySide6"]


def clean_egg_info():
    # After a successful bdist_wheel build, some .egg-info directories
    # are left over, which confuse pip when invoking it via
    # python -m pip, making pip think that the packages are already
    # installed in the root source directory.
    # Clean up the .egg-info directories to fix this, it should be
    # safe to do so.
    paths = find_files_using_glob(setup_script_dir, "*.egg-info")
    for p in paths:
        log.info(f"Removing {p}")
        rmtree(p)


def install_wheel(wheel_path):
    log.info(f"Installing wheel: {wheel_path}")
    exit_code = run_process([sys.executable, "-m", "pip", "install", wheel_path])
    log.info("")
    if exit_code:
        raise RuntimeError(f"Error while installing wheel {wheel_path}")


def try_install_wheels(wheels_dir, py_version):
    clean_egg_info()
    all_wheels_pattern = "*.whl"
    all_wheels = find_files_using_glob(wheels_dir, all_wheels_pattern)

    if len(all_wheels) > 1:
        log.info(f"Found the following wheels in {wheels_dir}: ")
        for wheel in all_wheels:
            log.info(wheel)
    else:
        log.info(f"No wheels found in {wheels_dir}")
    log.info("")

    for p in package_prefix_names():
        log.info(f"Trying to install {p}:")
        pattern = f"{p}-*cp{int(float(py_version))}*.whl"
        files = find_files_using_glob(wheels_dir, pattern)
        if files and len(files) == 1:
            wheel_path = files[0]
            install_wheel(wheel_path)
        elif len(files) > 1:
            raise RuntimeError(f"More than one wheel found for specific {p} version.")
        else:
            raise RuntimeError(
                f"No {p} wheels compatible with Python {py_version} found " f"for testing."
            )


def generate_build_cmake():
    # Specify prefix path so find_package(Qt6) works.
    qmake_dir = Path(QMAKE_PATH).resolve().parent.parent
    args = [CMAKE_PATH, "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release",
                        f"-Dpython_interpreter={sys.executable}",
                        f"-DCMAKE_PREFIX_PATH={qmake_dir}",
                        ".."]
    exit_code = run_process(args)
    if exit_code:
        raise RuntimeError("Failure while running cmake.")
    log.info("")


def raise_error_pyinstaller(msg):
    print()
    print(f"PYINST: {msg}")
    print(f"PYINST:   sys.version         = {sys.version.splitlines()[0]}")
    print(f"PYINST:   platform.platform() = {platform.platform()}")
    print("PYINST: See the error message above.")
    print()
    for line in run_process_output([sys.executable, "-m", "pip", "list"]):
        print(f"PyInstaller pip list:   {line}")
    print()
    raise (RuntimeError(msg))


def compile_using_pyinstaller():
    _ = os.path.join("..", "hello.py")
    spec_path = os.path.join("..", "hello_app.spec")
    exit_code = run_process([sys.executable, "-m", "PyInstaller", spec_path])
    # to create the spec file, this setting was used:
    # "--name=hello_app", "--console", "--log-level=DEBUG", src_path])
    # By using a spec file, we avoid all the probing that might disturb certain
    # platforms and also save some analysis time.
    if exit_code:
        # 2019-04-28 Raising on error is again enabled
        raise_error_pyinstaller("Failure while compiling script using PyInstaller.")
    log.info("")


def test_nuitka(example):
    testprog = "Nuitka"
    name = os.path.splitext(os.path.basename(example))[0]
    print(f"Running {testprog} test of {name}")
    current_dir = os.getcwd()
    result = False
    tmpdirname = tempfile.mkdtemp()
    try:
        os.chdir(tmpdirname)
        cmd = [sys.executable, "-m", "nuitka", "--run", example]  # , "--standalone"]
        _ = run_process(cmd)
        result = True
    except RuntimeError as e:
        print(str(e))
    finally:
        os.chdir(current_dir)
    print(f"Executable is in {tmpdirname}")
    return result


def run_nuitka_test(example):
    if test_nuitka(example):
        log.info("")
    else:
        raise RuntimeError(f"Failure running {example} with Nuitka.")


def run_ninja():
    args = ["ninja"]
    exit_code = run_process(args)
    if exit_code:
        raise RuntimeError(f"Failure while running {' '.join(args)}.")
    log.info("")


def run_ninja_install():
    args = ["ninja", "install"]
    exit_code = run_process(args)
    if exit_code:
        raise RuntimeError(f"Failed while running {' '.join(args)} install.")
    log.info("")


def run_compiled_script(binary_path):
    args = [binary_path]
    exit_code = run_process(args)
    if exit_code:
        raise_error_pyinstaller(f"Failure while executing compiled script: {binary_path}")
    log.info("")


def execute_script(script_path, *extra):
    args = list(map(str, (sys.executable, script_path) + extra))
    exit_code = run_process(args)
    if exit_code:
        raise RuntimeError(f"Failure while executing script: {script_path}")
    log.info("")


def prepare_build_folder(src_path, build_folder_name):
    build_path = os.path.join(src_path, build_folder_name)

    # The script can be called for Python 3 wheels, so
    # preparing a build folder should clean any previous existing build.
    if os.path.exists(build_path):
        log.info(f"Removing {build_path}")
        rmtree(build_path)

    log.info(f"Creating {build_path}")
    os.makedirs(build_path)
    os.chdir(build_path)


def try_build_examples():
    examples_dir = get_examples_dir()

    # Disabled PyInstaller until it supports PySide 6
    if False:
        # But because it is most likely to break, we put it here for now.
        log.info("Attempting to build hello.py using PyInstaller.")
        # PyInstaller is loaded by coin_build_instructions.py, but not when
        # testing directly this script.
        src_path = os.path.join(examples_dir, "installer_test")
        prepare_build_folder(src_path, "pyinstaller")
        compile_using_pyinstaller()
        run_compiled_script(os.path.join(src_path, "pyinstaller", "dist", "hello_app", "hello_app"))

    log.info("Attempting to build hello.py using Nuitka.")
    src_path = Path(examples_dir) / "installer_test"
    # Nuitka is loaded by coin_build_instructions.py, but not when
    # testing directly this script.
    run_nuitka_test(os.fspath(src_path / "hello.py"))

    log.info("Attempting to build and run samplebinding using cmake.")
    src_path = os.path.join(examples_dir, "samplebinding")
    prepare_build_folder(src_path, "cmake")
    generate_build_cmake()
    run_ninja()
    run_ninja_install()
    execute_script(os.path.join(src_path, "main.py"))

    log.info("Attempting to build scriptableapplication using cmake.")
    src_path = os.path.join(examples_dir, "scriptableapplication")
    prepare_build_folder(src_path, "cmake")
    generate_build_cmake()
    run_ninja()

    if sys.version_info[:2] >= (3, 7):
        log.info("Checking Python Interface Files in Python 3 with all features selected")
        with tempfile.TemporaryDirectory() as tmpdirname:
            src_path = Path(tmpdirname) / "pyi_test"
            pyi_script_dir = Path(setup_script_dir) / "sources" / "pyside6" / "PySide6" / "support"
            execute_script(
                pyi_script_dir / "generate_pyi.py",
                "all",
                "--outpath",
                src_path,
                "--feature",
                "snake_case",
                "true_property",
            )
            from PySide6 import __all__ as modules

            for modname in modules:
                execute_script(src_path / f"{modname}.pyi")


def run_wheel_tests(install_wheels, wheels_dir_name):
    wheels_dir = get_wheels_dir(wheels_dir_name)
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    if install_wheels:
        log.info("Attempting to install wheels.\n")
        try_install_wheels(wheels_dir, py_version)

    log.info("Attempting to build examples.\n")
    try_build_examples()

    log.info("All tests passed!")


if __name__ == "__main__":
    parser = ArgumentParser(description="wheel_tester", formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "--no-install-wheels",
        "-n",
        action="store_true",
        help="Do not install wheels" " (for developer builds with virtualenv)",
    )
    parser.add_argument("--qmake", type=str, help="Path to qmake")
    parser.add_argument("--cmake", type=str, help="Path to cmake")
    parser.add_argument("--wheels-dir", type=str, help="Path to where the wheels are", default="dist")
    parser.add_argument("--new", action="store_true", help="Option to test new wheels")
    options = parser.parse_args()
    QMAKE_PATH = find_executable("qmake", options.qmake)
    CMAKE_PATH = find_executable("cmake", options.cmake)
    NEW_WHEELS = options.new

    run_wheel_tests(not options.no_install_wheels, options.wheels_dir)
