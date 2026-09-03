# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool

import argparse
import logging
import shutil
import traceback
from pathlib import Path
from textwrap import dedent

from deploy_lib import (create_config_file, config_option_exists, PythonExecutable,
                        MAJOR_VERSION)
from deploy_lib.ios import IOSConfig, IOSData
from deploy_lib.ios import pbxproj, main_mm, info_plist, ios_dependency


""" pyside6-ios-deploy deployment tool

    Deployment tool that generates an Xcode project for a PySide6 application, statically
    linked against a cross-compiled PySide6/shiboken6 iOS wheel and BeeWare's
    Python-Apple-support Python.xcframework.

    Command: pyside6-ios-deploy --wheel-pyside=<pyside_wheel_path>
                                --wheel-shiboken=<shiboken_wheel_path>
                                --xcframework-path=<python_xcframework_path>

    Prerequisities: Python main entrypoint file should be named "main.py"

    Config file:
        On the first run of the tool, it creates a config file called pysidedeploy.spec which
        controls the various characteristics of the deployment, under the [ios] section.
        Edit this file directly to set the bundle id, team id, entitlements, signing style, etc.
"""


def main(name: str = None, wheel_pyside: Path = None, wheel_shiboken: Path = None,
         xcframework_path: Path = None, bundle_id: str = None, team_id: str = None,
         app_version: str = None, config_file: Path = None, init: bool = False,
         loglevel=logging.WARNING, dry_run: bool = False, force: bool = False):

    logging.basicConfig(level=loglevel)

    main_file = Path.cwd() / "main.py"
    if not main_file.exists():
        raise RuntimeError(
            "[DEPLOY] For iOS deployment to work, the main entrypoint Python file should be "
            "named 'main.py' and it should be run from the application directory"
        )

    ios_data = IOSData(wheel_pyside=wheel_pyside, wheel_shiboken=wheel_shiboken,
                       xcframework_path=xcframework_path)

    python = PythonExecutable(dry_run=dry_run, init=init, force=force)

    config_file_exists = config_file and Path(config_file).exists()

    if config_file_exists:
        logging.info(f"[DEPLOY] Using existing config file {config_file}")
    else:
        config_file = create_config_file(main_file=main_file, dry_run=dry_run)

    try:
        config = IOSConfig(config_file=config_file, source_file=main_file, python_exe=python.exe,
                           dry_run=dry_run, ios_data=ios_data,
                           existing_config_file=config_file_exists, name=name,
                           bundle_id=bundle_id, team_id=team_id, app_version=app_version)
    except RuntimeError as e:
        print(e)
        return

    if not dry_run:
        config.update_config()

    if init:
        logging.info(f"[DEPLOY] Config file {config.config_file} created")
        return

    try:
        out_dir = config.output_dir
        product_name = config.name.replace(" ", "")
        proj_dir = out_dir / f"{product_name}.xcodeproj"
        proj_dir.mkdir(parents=True, exist_ok=True)

        qml_plugins = ios_dependency.resolve_qml_plugins(config, config.qml_qt_modules)
        plugins = ios_dependency.enabled_plugins(config)
        qml_plugin_paths = [
            str(p.archive_path.relative_to(config.qt_ios)) for p in qml_plugins
        ]
        qt_deps = ios_dependency.resolve_qt_dependencies(
            config, config.qt_modules, plugin_paths=plugins + qml_plugin_paths
        )

        main_mm_path = out_dir / "main.mm"
        main_mm_path.write_text(main_mm.generate(config, qml_plugins, qt_deps))
        logging.info(f"[DEPLOY] Wrote {main_mm_path}")

        info_plist_path = out_dir / "Info.plist"
        info_plist_path.write_bytes(info_plist.generate(config))
        logging.info(f"[DEPLOY] Wrote {info_plist_path}")

        if config.entitlements:
            entitlements_src = config.project_root / config.entitlements
            entitlements_dest = out_dir / Path(config.entitlements).name
            shutil.copyfile(entitlements_src, entitlements_dest)
            logging.info(f"[DEPLOY] Copied {entitlements_src} -> {entitlements_dest}")

        pbxproj_path = proj_dir / "project.pbxproj"
        pbxproj_path.write_text(pbxproj.generate(config, qml_plugins, qt_deps))
        logging.info(f"[DEPLOY] Wrote {pbxproj_path}")

        logging.info(f"[DEPLOY] Done. Open with:\n  open {proj_dir}")
    except Exception:
        print(f"Exception occurred: {traceback.format_exc()}")

    logging.info("[DEPLOY] End")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=dedent(f"""
                           This tool generates an Xcode project to deploy PySide{MAJOR_VERSION}
                           applications to iOS.

                           Note: The main python entrypoint should be named main.py
                           """),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-c", "--config-file", type=lambda p: Path(p).absolute(),
                        default=(Path.cwd() / "pysidedeploy.spec"),
                        help="Path to the .spec config file")

    parser.add_argument(
        "--init", action="store_true",
        help="Only create/update pysidedeploy.spec, without generating the Xcode project. "
        "(pysidedeploy.spec is always created/updated regardless of this flag; this just "
        "skips the actual generation step.)")

    parser.add_argument(
        "-v", "--verbose", help="run in verbose mode", action="store_const",
        dest="loglevel", const=logging.INFO)

    parser.add_argument("--dry-run", action="store_true", help="show the commands to be run")

    parser.add_argument("-f", "--force", action="store_true", help="force all input prompts")

    parser.add_argument("--name", type=str, help="Application name")

    parser.add_argument("--wheel-pyside", type=lambda p: Path(p).resolve(),
                        help=f"Path to PySide{MAJOR_VERSION} iOS wheel",
                        required=not config_option_exists())

    parser.add_argument("--wheel-shiboken", type=lambda p: Path(p).resolve(),
                        help=f"Path to shiboken{MAJOR_VERSION} iOS wheel",
                        required=not config_option_exists())

    parser.add_argument("--xcframework-path", type=lambda p: Path(p).resolve(),
                        help="Path to Python's iOS Python.xcframework",
                        required=not config_option_exists())

    parser.add_argument("--bundle-id", type=str,
                        help="Reverse-DNS bundle identifier, eg: com.example.myapp. Default: "
                        "derived from the app name, eg: com.example.MyApp")

    parser.add_argument("--team-id", type=str,
                        help="Apple Developer Team ID, used for code signing. Only required "
                        "for device builds")

    parser.add_argument("--app-version", type=str, help="App version (CFBundleShortVersionString)")

    args = parser.parse_args()

    main(args.name, args.wheel_pyside, args.wheel_shiboken, args.xcframework_path,
         args.bundle_id, args.team_id, args.app_version, args.config_file, args.init,
         args.loglevel, args.dry_run, args.force)
