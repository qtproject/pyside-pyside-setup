# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import logging
import argparse
import stat
import warnings
import shutil
from dataclasses import dataclass

from pathlib import Path
from git import Repo, RemoteProgress
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader

from android_utilities import (run_command, download_android_commandlinetools,
                               download_android_ndk, install_android_packages)

# Note: Does not work with PyEnv. Your Host Python should contain openssl.
# also update the version in ShibokenHelpers.cmake if Python version changes.
PYTHON_VERSION = "3.11"

SKIP_UPDATE_HELP = ("skip the updation of SDK packages build-tools, platform-tools to"
                    " latest version")

ACCEPT_LICENSE_HELP = ('''
Accepts license automatically for Android SDK installation. Otherwise,
accept the license manually through command line.
''')

CLEAN_CACHE_HELP = ('''
Cleans cache stored in $HOME/.pyside6_deploy_cache.
Options:

1. all - all the cache including Android Ndk, Android Sdk and Cross-compiled Python are deleted.
2. ndk - Only the Android Ndk is deleted.
3. sdk - Only the Android Sdk is deleted.
4. python - The cross compiled Python for all platforms, the cloned CPython, the cross compilation
            scripts for all platforms are deleted.
5. toolchain - The CMake toolchain file required for cross-compiling Qt for Python, for all
               platforms are deleted.

If --clean-cache is used and no explicit value is suppied, then `all` is used as default.
''')


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This tool cross builds CPython for Android and uses that Python to cross build"
                    "Android Qt for Python wheels",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-p", "--plat-name", type=str, nargs="*",
                        choices=["aarch64", "armv7a", "i686", "x86_64"],
                        default=["aarch64", "armv7a", "i686", "x86_64"], dest="plat_names",
                        help="Android target platforms")

    parser.add_argument("-v", "--verbose", help="run in verbose mode", action="store_const",
                        dest="loglevel", const=logging.INFO)
    parser.add_argument("--api-level", type=str, default="26",
                        help="Minimum Android API level to use")
    parser.add_argument("--ndk-path", type=str, help="Path to Android NDK (Preferred r25c)")
    # sdk path is needed to compile all the Qt Java Acitivity files into Qt6AndroidBindings.jar
    parser.add_argument("--sdk-path", type=str, help="Path to Android SDK")
    parser.add_argument("--qt-install-path", type=str, required=not occp_exists(),
                        help="Qt installation path eg: /home/Qt/6.5.0")

    parser.add_argument("-occp", "--only-cross-compile-python", action="store_true",
                        help="Only cross compiles Python for the specified Android platform")

    parser.add_argument("--dry-run", action="store_true", help="show the commands to be run")

    parser.add_argument("--skip-update", action="store_true",
                        help=SKIP_UPDATE_HELP)

    parser.add_argument("--auto-accept-license", action="store_true",
                        help=ACCEPT_LICENSE_HELP)

    parser.add_argument("--clean-cache", type=str, nargs="?", const="all",
                        choices=["all", "python", "ndk", "sdk", "toolchain"],
                        help=CLEAN_CACHE_HELP)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    pyside_setup_dir = Path(__file__).parents[2].resolve()
    qt_install_path = args.qt_install_path
    ndk_path = args.ndk_path
    sdk_path = args.sdk_path
    only_py_cross_compile = args.only_cross_compile_python
    android_abi = None
    gcc_march = None
    plat_bits = None
    dry_run = args.dry_run
    plat_names = args.plat_names
    api_level = args.api_level
    skip_update = args.skip_update
    auto_accept_license = args.auto_accept_license
    clean_cache = args.clean_cache

    # auto download Android NDK and SDK
    pyside6_deploy_cache = Path.home() / ".pyside6_android_deploy"
    logging.info(f"Cache created at {str(pyside6_deploy_cache.resolve())}")
    pyside6_deploy_cache.mkdir(exist_ok=True)

    if pyside6_deploy_cache.exists() and clean_cache:
        if clean_cache == "all":
            shutil.rmtree(pyside6_deploy_cache)
        elif clean_cache == "ndk":
            cached_ndk_dir = pyside6_deploy_cache / "android-ndk"
            if cached_ndk_dir.exists():
                shutil.rmtree(cached_ndk_dir)
        elif clean_cache == "sdk":
            cached_sdk_dir = pyside6_deploy_cache / "android-sdk"
            if cached_sdk_dir.exists():
                shutil.rmtree(cached_sdk_dir)
        elif clean_cache == "python":
            cached_cpython_dir = pyside6_deploy_cache / "cpython"
            if cached_cpython_dir.exists():
                shutil.rmtree(pyside6_deploy_cache / "cpython")
            for cc_python_path in pyside6_deploy_cache.glob("Python-*"):
                if cc_python_path.is_dir():
                    shutil.rmtree(cc_python_path)
        elif clean_cache == "toolchain":
            for toolchain_path in pyside6_deploy_cache.glob("toolchain_*"):
                if toolchain_path.is_file():
                    toolchain_path.unlink()

    if not ndk_path:
        # Download android ndk
        ndk_path = download_android_ndk(pyside6_deploy_cache)

    if not sdk_path:
        # download and unzip command-line tools
        sdk_path = download_android_commandlinetools(pyside6_deploy_cache)
        # install and update required android packages
        install_android_packages(android_sdk_dir=sdk_path, android_api=api_level, dry_run=dry_run,
                                 accept_license=auto_accept_license, skip_update=skip_update)

    templates_path = Path(__file__).parent / "templates"

    for plat_name in plat_names:
        # for armv7a the API level dependent binaries like clang are named
        # armv7a-linux-androideabi27-clang, as opposed to other platforms which
        # are named like x86_64-linux-android27-clang
        platform_data = None
        if plat_name == "armv7a":
            platform_data = PlatformData("armv7a", api_level, "armeabi-v7a", "armv7",
                                         "armv7", "32")
        elif plat_name == "aarch64":
            platform_data = PlatformData("aarch64", api_level, "arm64-v8a", "arm64_v8a", "armv8-a",
                                         "64")
        elif plat_name == "i686":
            platform_data = PlatformData("i686", api_level, "x86", "x86", "i686", "32")
        else:  # plat_name is x86_64
            platform_data = PlatformData("x86_64", api_level, "x86_64", "x86_64", "x86-64", "64")

        # python path is valid, if Python for android installation exists in python_path
        python_path = (pyside6_deploy_cache
                       / f"Python-{platform_data.plat_name}-linux-android" / "_install")
        valid_python_path = python_path.exists()
        if Path(python_path).exists():
            expected_dirs = ["lib", "include"]
            for expected_dir in expected_dirs:
                if not (Path(python_path) / expected_dir).is_dir():
                    valid_python_path = False
                    warnings.warn(
                        f"{str(python_path.resolve())} is corrupted. New Python for {plat_name} "
                        f"android will be cross-compiled into {str(pyside6_deploy_cache.resolve())}"
                    )
                    break

        environment = Environment(loader=FileSystemLoader(templates_path))
        if not valid_python_path:
            # clone cpython and checkout 3.10
            cpython_dir = pyside6_deploy_cache / "cpython"
            python_ccompile_script = cpython_dir / f"cross_compile_{plat_name}.sh"

            if not cpython_dir.exists():
                logging.info(f"cloning cpython {PYTHON_VERSION}")
                Repo.clone_from(
                    "https://github.com/python/cpython.git",
                    cpython_dir,
                    progress=CloneProgress(),
                    branch=PYTHON_VERSION,
                )

            if not python_ccompile_script.exists():
                host_system_config_name = run_command("./config.guess", cwd=cpython_dir,
                                                      dry_run=dry_run, show_stdout=True,
                                                      capture_stdout=True).strip()

                # use jinja2 to create cross_compile.sh script
                template = environment.get_template("cross_compile.tmpl.sh")
                content = template.render(
                    plat_name=platform_data.plat_name,
                    ndk_path=ndk_path,
                    api_level=platform_data.api_level,
                    android_py_install_path_prefix=pyside6_deploy_cache,
                    host_python_path=sys.executable,
                    python_version=PYTHON_VERSION,
                    host_system_name=host_system_config_name,
                    host_platform_name=sys.platform
                )

                logging.info(f"Writing Python cross compile script into {python_ccompile_script}")
                with open(python_ccompile_script, mode="w", encoding="utf-8") as ccompile_script:
                    ccompile_script.write(content)

                # give run permission to cross compile script
                python_ccompile_script.chmod(python_ccompile_script.stat().st_mode | stat.S_IEXEC)

            # clean built files
            logging.info("Cleaning CPython built files")
            run_command(["make", "distclean"], cwd=cpython_dir, dry_run=dry_run, ignore_fail=True)

            # run the cross compile script
            logging.info(f"Running Python cross-compile for platform {platform_data.plat_name}")
            run_command([f"./{python_ccompile_script.name}"], cwd=cpython_dir, dry_run=dry_run,
                        show_stdout=True)

            logging.info(
                f"Cross compile Python for Android platform {platform_data.plat_name}. "
                f"Final installation in {python_path}"
            )

            if only_py_cross_compile:
                continue

        if only_py_cross_compile:
            requested_platforms = ",".join(plat_names)
            print(f"Python for Android platforms: {requested_platforms} cross compiled "
                  f"to {str(pyside6_deploy_cache)}")
            sys.exit(0)

        qfp_toolchain = pyside6_deploy_cache / f"toolchain_{platform_data.plat_name}.cmake"

        if not qfp_toolchain.exists():
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

            logging.info(f"Writing Qt for Python toolchain file into {qfp_toolchain}")
            with open(qfp_toolchain, mode="w", encoding="utf-8") as ccompile_script:
                ccompile_script.write(content)

            # give run permission to cross compile script
            qfp_toolchain.chmod(qfp_toolchain.stat().st_mode | stat.S_IEXEC)

        if sys.platform == "linux":
            host_qt_install_suffix = "gcc_64"
        elif sys.platform == "darwin":
            host_qt_install_suffix = "macos"
        else:
            raise RuntimeError("Qt for Python cross compilation not supported on this platform")

        # run the cross compile script
        logging.info(f"Running Qt for Python cross-compile for platform {platform_data.plat_name}")
        qfp_ccompile_cmd = [sys.executable, "setup.py", "bdist_wheel", "--parallel=9",
                            "--standalone",
                            f"--cmake-toolchain-file={str(qfp_toolchain.resolve())}",
                            f"--qt-host-path={qt_install_path}/{host_qt_install_suffix}",
                            f"--plat-name=android_{platform_data.plat_name}",
                            f"--python-target-path={python_path}",
                            (f"--qt-target-path={qt_install_path}/"
                             f"android_{platform_data.qt_plat_name}"),
                            "--no-qt-tools"]
        run_command(qfp_ccompile_cmd, cwd=pyside_setup_dir, dry_run=dry_run, show_stdout=True)
