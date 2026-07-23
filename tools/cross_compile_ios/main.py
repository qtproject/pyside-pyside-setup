# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import argparse
import sys
import os
import subprocess
from pathlib import Path

from ios_utilities import (download_python_support,
                           generate_toolchain,
                           python_xcframework_slice_dir,
                           PYSIDE_SETUP_ROOT)


def cmd_build(args: argparse.Namespace) -> None:
    """ Build subcommand """
    simulator = args.simulator or (args.arch == "x86_64")
    arch = args.arch
    qt_install_path = args.qt_install_path.expanduser().resolve()
    qt_ios = qt_install_path / "ios"
    qt_macos = qt_install_path / "macos"

    # Download BeeWare Python.xcframework
    python_xcframework = download_python_support()

    # Generate toolchain file
    toolchain = generate_toolchain(
        arch=arch,
        simulator=simulator,
        python_xcframework=python_xcframework,
        qt_ios=qt_ios,
    )

    # Cross-compile PySide6
    suffix = f"{arch}_simulator" if simulator else arch
    plat_name = f"ios_{suffix}"
    python_slice = python_xcframework / python_xcframework_slice_dir(arch, simulator)
    cmd = [
        sys.executable, "setup.py", "build",
        "--standalone",
        f"--cmake-toolchain-file={toolchain}",
        f"--qt-host-path={qt_macos}",
        f"--qt-target-path={qt_ios}",
        f"--python-target-path={python_slice}",
        f"--plat-name={plat_name}",
        "--no-qt-tools",
    ]

    env = os.environ.copy()
    logging.info(f"Running bdist_wheel for platform {plat_name}")
    subprocess.run(cmd, cwd=PYSIDE_SETUP_ROOT, env=env, check=True)


def cmd_generate(args: argparse.Namespace) -> None:
    """ Generate subcommand """
    # TODO: Xcode project generation
    logging.error("The 'generate' command (Xcode project generation) isn't implemented yet.")
    sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="PySide6 iOS cross-compilation tools",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- build ---
    build_p = subparsers.add_parser(
        "build",
        help="Cross-compile PySide6 for iOS",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    build_p.add_argument(
        "--qt-install-path", required=True, type=Path,
        help="Qt installation root, e.g. ~/Qt/6.11.0",
    )
    build_p.add_argument(
        "--arch", choices=["arm64", "x86_64"], default="arm64",
        help="Target CPU architecture (default: arm64; x86_64 implies --simulator)",
    )
    build_p.add_argument(
        "--simulator", action="store_true",
        help="Build for iOS Simulator (device is the default)",
    )

    # --- generate ---
    gen_p = subparsers.add_parser(
        "generate",
        help="Generate an Xcode project from a pyside6-ios.toml config",
    )
    gen_p.add_argument(
        "-c", "--config", required=True, type=Path,
        help="Path to the app config file (pyside6-ios.toml)",
    )

    args = parser.parse_args()

    if args.command == "build":
        cmd_build(args)
    elif args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
