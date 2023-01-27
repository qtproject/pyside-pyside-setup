# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import logging
import argparse
import tempfile
import subprocess
import stat
import warnings

from typing import List

from pathlib import Path
from git import Repo, RemoteProgress
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader

PYTHON_VERSION = "3.10"


def occp_exists():
    '''
    check if '--only-cross-compile-python' exists in command line arguments
    '''
    return "-occp" in sys.argv or "--only-cross-compile-python" in sys.argv


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=""):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def run_command(command: List[str], cwd: str = None, ignore_fail: bool = False):
    ex = subprocess.call(command, cwd=cwd, shell=True)
    if ex != 0 and not ignore_fail:
        sys.exit(ex)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This tool cross builds cpython for android and uses that Python to cross build"
                    "android Qt for Python wheels",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-p", "--plat-name", type=str, required=True,
                        choices=["aarch64", "armv7a", "i686", "x86_64"],
                        help="Android target platform name")

    parser.add_argument("-v", "--verbose", help="run in verbose mode", action="store_const",
                        dest="loglevel", const=logging.INFO)
    parser.add_argument("--api-level", type=str, default="27", help="Android API level to use")
    parser.add_argument(
        "--ndk-path", type=str, required=True, help="Path to Android NDK (Preferred 23b)"
    )

    parser.add_argument("-occp", "--only-cross-compile-python", action="store_true",
                        help="Only cross compiles Python for the specified Android platform")

    parser.add_argument("-apic", "--android-python-install-path", type=str, default=None,
                        required=occp_exists(),
                        help='''
                        Points to the installation path of Python for the specific Android
                        platform. If the path given does not exist, then Python for android
                        is cross compiled for the specific platform and installed into this
                        path as <path>/Python-'plat_name'/_install.

                        If this path is not given, then Python for android is cross-compiled
                        into a temportary directory, which is deleted when the Qt for Python
                        android wheels are created.
                        ''')

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    current_dir = Path.cwd()
    ndk_path = args.ndk_path
    only_py_cross_compile = args.only_cross_compile_python
    python_path = args.android_python_install_path

    # python path is valid, if Python for android installation exists in python_path
    valid_python_path = True
    if python_path and Path(python_path).exists():
        expected_dirs = ["lib", "include"]
        for expected_dir in expected_dirs:
            if not (Path(python_path) / expected_dir).is_dir():
                valid_python_path = False
                warnings.warn(
                    "Given target Python, given through --android-python-install-path does not"
                    "contain Python. New Python for android will be cross compiled and installed"
                    "in this directory"
                )
                break

    templates_path = Path(__file__).parent / "templates"
    plat_name = args.plat_name
    api_level = args.api_level

    # for armv7a the API level dependent binaries like clang are named
    # armv7a-linux-androideabi27-clang, as opposed to other platforms which
    # are named like x86_64-linux-android27-clang
    if plat_name == "armv7a":
        api_level = f"eabi{api_level}"

    # clone cpython and checkout 3.10
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        logging.info(f"temp dir created at {temp_dir}")
        if not python_path or not valid_python_path:
            cpython_dir = temp_dir / "cpython"
            python_ccompile_script = cpython_dir / "cross_compile.sh"

            logging.info(f"cloning cpython {PYTHON_VERSION}")
            Repo.clone_from(
                "https://github.com/python/cpython.git",
                cpython_dir,
                progress=CloneProgress(),
                branch=PYTHON_VERSION,
            )

            if not python_path:
                android_py_install_path_prefix = temp_dir
            else:
                android_py_install_path_prefix = python_path

            # use jinja2 to create cross_compile.sh script
            environment = Environment(loader=FileSystemLoader(templates_path))
            template = environment.get_template("cross_compile.tmpl.sh")
            content = template.render(
                plat_name=plat_name,
                ndk_path=ndk_path,
                api_level=api_level,
                android_py_install_path_prefix=android_py_install_path_prefix,
            )

            logging.info(f"Writing Python cross compile script into {python_ccompile_script}")
            with open(python_ccompile_script, mode="w", encoding="utf-8") as ccompile_script:
                ccompile_script.write(content)

            # give run permission to cross compile script
            python_ccompile_script.chmod(python_ccompile_script.stat().st_mode | stat.S_IEXEC)

            # run the cross compile script
            logging.info(f"Running Python cross-compile for platform {plat_name}")
            run_command(["./cross_compile.sh"], cwd=cpython_dir)

            python_path = (f"{android_py_install_path_prefix}/Python-{plat_name}-linux-android/"
                           "_install")

            # run patchelf to change the SONAME of libpython from libpython3.x.so.1.0 to
            # libpython3.x.so, to match with python_for_android's Python library. Otherwise,
            # the Qfp binaries won't be able to link to Python
            run_command(["patchelf", "--set-soname", f"libpython{PYTHON_VERSION}.so.1.0",
                         f"libpython{PYTHON_VERSION}.so"], cwd=Path(python_path) / "lib")

            logging.info(
                f"Cross compile Python for Android platform {plat_name}."
                f"Final installation in "
                f"{python_path}"
            )

            if only_py_cross_compile:
                sys.exit(0)
