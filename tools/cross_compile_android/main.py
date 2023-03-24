# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import logging
import argparse
import tempfile
import subprocess
import stat
import warnings
from dataclasses import dataclass
from typing import List

from pathlib import Path
from git import Repo, RemoteProgress
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader

# Note: Does not work with PyEnv. Your Host Python should contain openssl.
PYTHON_VERSION = "3.10"


@dataclass
class PlatformData:
    plat_name: str
    api_level: str
    android_abi: str
    qt_plat_name: str
    gcc_march: str
    plat_bits: str


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


def run_command(command: List[str], cwd: str = None, ignore_fail: bool = False,
                dry_run: bool = False):
    if dry_run:
        print(" ".join(command))
        return
    ex = subprocess.call(command, cwd=cwd)
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
    parser.add_argument("--api-level", type=str, default="31", help="Android API level to use")
    parser.add_argument("--ndk-path", type=str, required=True,
                        help="Path to Android NDK (Preferred 25b)")
    # sdk path is needed to compile all the Qt Java Acitivity files into Qt6AndroidBindings.jar
    parser.add_argument("--sdk-path", type=str, required=True,
                        help="Path to Android SDK")
    parser.add_argument("--qt-install-path", type=str, required=not occp_exists(),
                        help="Qt installation path eg: /home/Qt/6.5.0")

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

    parser.add_argument("--dry-run", action="store_true", help="show the commands to be run")

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    pyside_setup_dir = Path(__file__).parents[2].resolve()
    qt_install_path = args.qt_install_path
    ndk_path = args.ndk_path
    sdk_path = args.sdk_path
    only_py_cross_compile = args.only_cross_compile_python
    python_path = args.android_python_install_path
    # the same android platforms are named differently in CMake, Cpython and Qt.
    # Hence, we need to distinguish them
    qt_plat_name = None
    android_abi = None
    gcc_march = None
    plat_bits = None
    dry_run = args.dry_run

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
    platform_data = None
    if plat_name == "armv7a":
        platform_data = PlatformData("armv7a", f"eabi{api_level}", "armeabi-v7a", "armv7", "armv7",
                                     "32")
    elif plat_name == "aarch64":
        platform_data = PlatformData("aarch64", api_level, "arm64-v8a", "arm64_v8a", "armv8-a", "64")
    elif plat_name == "i686":
        platform_data = PlatformData("i686", api_level, "x86", "x86", "i686", "32")
    else:  # plat_name is x86_64
        platform_data = PlatformData("x86_64", api_level, "x86_64", "x86_64", "x86-64", "64")

    # clone cpython and checkout 3.10
    with tempfile.TemporaryDirectory() as temp_dir:
        environment = Environment(loader=FileSystemLoader(templates_path))
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
            template = environment.get_template("cross_compile.tmpl.sh")
            content = template.render(
                plat_name=platform_data.plat_name,
                ndk_path=ndk_path,
                api_level=platform_data.api_level,
                android_py_install_path_prefix=android_py_install_path_prefix,
            )

            logging.info(f"Writing Python cross compile script into {python_ccompile_script}")
            with open(python_ccompile_script, mode="w", encoding="utf-8") as ccompile_script:
                ccompile_script.write(content)

            # give run permission to cross compile script
            python_ccompile_script.chmod(python_ccompile_script.stat().st_mode | stat.S_IEXEC)

            # run the cross compile script
            logging.info(f"Running Python cross-compile for platform {platform_data.plat_name}")
            run_command(["./cross_compile.sh"], cwd=cpython_dir, dry_run=dry_run)

            python_path = (f"{android_py_install_path_prefix}/Python-{platform_data.plat_name}-linux-android/"
                           "_install")

            # run patchelf to change the SONAME of libpython from libpython3.x.so.1.0 to
            # libpython3.x.so, to match with python_for_android's Python library. Otherwise,
            # the Qfp binaries won't be able to link to Python
            run_command(["patchelf", "--set-soname", f"libpython{PYTHON_VERSION}.so",
                         f"libpython{PYTHON_VERSION}.so.1.0"], cwd=Path(python_path) / "lib")

            logging.info(
                f"Cross compile Python for Android platform {platform_data.plat_name}. "
                f"Final installation in "
                f"{python_path}"
            )

            if only_py_cross_compile:
                sys.exit(0)

        qfp_toolchain = temp_dir / f"toolchain_{platform_data.plat_name}.cmake"
        template = environment.get_template("toolchain_default.tmpl.cmake")
        content = template.render(
            ndk_path=ndk_path,
            sdk_path=sdk_path,
            api_level=platform_data.api_level,
            qt_install_path=qt_install_path,
            plat_name=platform_data.plat_name,
            android_abi=platform_data.android_abi,
            qt_plat_name=platform_data.qt_plat_name,
            gcc_march=platform_data.gcc_march,
            plat_bits=platform_data.plat_bits,
            python_version=PYTHON_VERSION,
            target_python_path=python_path
        )

        logging.info(f"Writing Qt for Python toolchain file into"
                     f"{qfp_toolchain}")
        with open(qfp_toolchain, mode="w", encoding="utf-8") as ccompile_script:
            ccompile_script.write(content)

        # give run permission to cross compile script
        qfp_toolchain.chmod(qfp_toolchain.stat().st_mode | stat.S_IEXEC)

        # run the cross compile script
        logging.info(f"Running Qt for Python cross-compile for platform {platform_data.plat_name}")
        qfp_ccompile_cmd = [sys.executable, "setup.py", "bdist_wheel", "--parallel=9",
                            "--ignore-git", "--standalone", "--limited-api=yes",
                            f"--cmake-toolchain-file={str(qfp_toolchain.resolve())}",
                            f"--qt-host-path={qt_install_path}/gcc_64",
                            f"--plat-name=android_{platform_data.plat_name}",
                            f"--python-target-path={python_path}",
                            (f"--qt-target-path={qt_install_path}/"
                             f"android_{platform_data.qt_plat_name}"),
                            "--no-qt-tools", "--skip-docs"]
        run_command(qfp_ccompile_cmd, cwd=pyside_setup_dir, dry_run=dry_run)
