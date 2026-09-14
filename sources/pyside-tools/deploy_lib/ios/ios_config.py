# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:critical reason:handling-untrusted-data

import logging
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from .. import Config
from ..dependency_util import get_py_files
from .ios_helper import (IOSData, get_wheel_ios_target, get_xcframework_python_version,
                         safe_extractall)
from .python_xcframework import download_python_support


def _unpack_wheel(wheel_path: Path, dest_parent: Path, package_name: str) -> Path:
    """
    Unpack a wheel's <package_name>/ directory into dest_parent, caching
    on dest_parent/<package_name> already existing (wheels can be large and
    generate() is meant to be re-run often).
    """
    dest = dest_parent / package_name
    if dest.is_dir():
        return dest
    dest_parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(wheel_path) as archive:
        safe_extractall(archive, dest_parent)
    return dest


def _version_tuple(v: str, what: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in v.split("."))
    except ValueError:
        raise RuntimeError(
            f"[DEPLOY] {what} is not a valid iOS version: \"{v}\" -- expected digits "
            "separated by dots, eg: \"18.0\""
        ) from None


def _qt_deployment_target(qt_ios: Path) -> str | None:
    """Read CMAKE_OSX_DEPLOYMENT_TARGET from Qt's own iOS toolchain file"""
    toolchain = qt_ios / "lib" / "cmake" / "Qt6" / "qt.toolchain.cmake"
    if not toolchain.is_file():
        return None
    m = re.search(
        r'set\(CMAKE_OSX_DEPLOYMENT_TARGET\s+"([\d.]+)"', toolchain.read_text()
    )
    return m.group(1) if m else None


# Apple's Mach-O LC_BUILD_VERSION platform codes
_PLATFORM_IOS = 2   # device
_PLATFORM_IOS_SIMULATOR = 7  # simulator
_PLATFORM_NAMES = {_PLATFORM_IOS: "device", _PLATFORM_IOS_SIMULATOR: "simulator"}


def _slice_platform(binary: Path, arch: str) -> int | None:
    """
    The LC_BUILD_VERSION platform code for one arch slice of a Mach-O
    binary or static archive (each member .o carries its own copy; they're
    all expected to agree, so the first match is used). Returns None if
    that arch slice doesn't exist in the binary at all.
    """
    try:
        output = subprocess.run(
            ["otool", "-arch", arch, "-l", str(binary)],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None
    except OSError as e:
        raise ValueError(f"Failed to inspect {binary}: {e}") from e

    m = re.search(r"LC_BUILD_VERSION\n\s+cmdsize \d+\n\s+platform (\d+)", output)
    return int(m.group(1)) if m else None


def _check_binary_matches_target(binary: Path, arch: str, simulator: bool, what: str) -> None:
    platform = _slice_platform(binary, arch)
    target = "simulator" if simulator else "device"
    if platform is None:
        raise ValueError(
            f"{binary} does not contain an {arch} slice -- {what} doesn't "
            f"have the architecture needed for the requested {target} target."
        )
    expected_platform = _PLATFORM_IOS_SIMULATOR if simulator else _PLATFORM_IOS
    if platform != expected_platform:
        actual = _PLATFORM_NAMES.get(platform, f"platform {platform}")
        raise ValueError(
            f"{binary}'s {arch} slice was built for {actual}, not {target} -- "
            f"{what} doesn't match the requested target."
        )


def _default_bundle_id(name: str) -> str:
    """
    Xcode-style placeholder: 'com.example.<ProductName>', with the app
    name stripped down to what a bundle id segment actually allows
    (alphanumeric and hyphen, per Apple's CFBundleIdentifier rules).
    Meant to be overridden before App Store distribution, same as Xcode's
    own default organization identifier.
    """
    sanitized = re.sub(r"[^A-Za-z0-9-]", "", name).strip("-") or "App"
    return f"com.example.{sanitized}"


class IOSConfig(Config):
    """Wrapper class around pysidedeploy.spec file for pyside6-ios-deploy"""
    def __init__(self, config_file: Path, source_file: Path, dry_run: bool, ios_data: IOSData,
                 existing_config_file: bool = False, name: str = None,
                 bundle_id: str = None, team_id: str = None, app_version: str = None):
        super().__init__(config_file=config_file, source_file=source_file, dry_run=dry_run,
                         existing_config_file=existing_config_file, name=name)

        if ios_data.wheel_pyside:
            self.wheel_pyside = ios_data.wheel_pyside
        else:
            wheel_pyside_temp = self.get_value("ios", "wheel_pyside")
            if not wheel_pyside_temp:
                raise RuntimeError("[DEPLOY] Unable to find PySide6 iOS wheel")
            self.wheel_pyside = Path(wheel_pyside_temp).resolve()

        if ios_data.wheel_shiboken:
            self.wheel_shiboken = ios_data.wheel_shiboken
        else:
            wheel_shiboken_temp = self.get_value("ios", "wheel_shiboken")
            if not wheel_shiboken_temp:
                raise RuntimeError("[DEPLOY] Unable to find shiboken6 iOS wheel")
            self.wheel_shiboken = Path(wheel_shiboken_temp).resolve()

        if ios_data.xcframework_path:
            self.xcframework_path = ios_data.xcframework_path
        else:
            # from config
            xcframework_temp = self.get_value("ios", "xcframework_path")
            if xcframework_temp:
                self.xcframework_path = Path(xcframework_temp).resolve()
            else:
                # download Python.xcframework
                self.xcframework_path = download_python_support(dry_run=dry_run)

        # arch/simulator are never given via cli -- the wheel's platform tag already
        # fixes them (eg: '...-ios_arm64_simulator.whl'), same as Android's
        # AndroidConfig._find_arch() deriving arch from the wheel name alone.
        wheel_target = get_wheel_ios_target(self.wheel_pyside)
        # TODO: check if there is a mismatch between shiboken and pyside
        if not wheel_target:
            raise RuntimeError(
                f"[DEPLOY] Unable to determine target architecture from "
                f"{self.wheel_pyside.name} -- expected a platform tag like "
                f"'ios_arm64' or 'ios_arm64_simulator'"
            )
        self.arch, self.simulator = wheel_target

        _check_binary_matches_target(self.qt_ios / "lib" / "QtCore.framework" / "QtCore",
                                     self.arch, self.simulator, "this PySide6 wheel's bundled Qt")

        modls = self.get_value("qt", "modules")
        if modls:
            self._modules = modls.split(",")
        else:
            modls = self._find_pysidemodules()
            modls += self._find_qtquick_modules()
            self.modules = list(set(modls))

        existing_bundle_id = self.get_value("ios", "bundle_id")
        if name and not bundle_id and existing_bundle_id:
            logging.warning(f"[DEPLOY] --name changed but bundle_id '{existing_bundle_id}' is "
                            "unchanged (pass --bundle-id to change it)")
        bundle_id = bundle_id or existing_bundle_id or _default_bundle_id(self.title)
        self.bundle_id = self.set_or_fetch(bundle_id, "bundle_id", "ios")
        if team_id:
            self.set_value("ios", "team_id", team_id)
        self.team_id = team_id or self.get_value("ios", "team_id") or ""
        self.version = self.set_or_fetch(app_version, "version", "ios")
        python_version = get_xcframework_python_version(self.xcframework_path)
        if not python_version:
            raise RuntimeError(
                f"[DEPLOY] Unable to determine the Python version from "
                f"{self.xcframework_path} -- expected a 'lib/python3.XX' directory inside it"
            )
        self.python_version = python_version
        self.signing_style = self.get_value("ios", "signing_style") or "Automatic"
        self.entitlements = self.get_value("ios", "entitlements") or ""

        header_search_paths = self.get_value("ios", "header_search_paths")
        self.header_search_paths = header_search_paths.split(",") if header_search_paths else []

        # Left empty in the spec, [ios] deployment_target follows whatever the Qt kit
        # in the wheel was built for. It is deliberately never written back, so that
        # empty keeps meaning "follow Qt" across Qt upgrades, and any value in there
        # is known to be the user's own.
        deployment_target = self.get_value("ios", "deployment_target")
        qt_min_deployment_target = _qt_deployment_target(self.qt_ios)
        target_source = "pysidedeploy.spec"
        if not deployment_target:
            deployment_target = qt_min_deployment_target
            target_source = "the Qt kit in the PySide6 wheel"
        if deployment_target is None:
            raise RuntimeError(
                "[DEPLOY] Could not determine Qt's minimum iOS deployment target from "
                f"{self.qt_ios / 'lib' / 'cmake' / 'Qt6' / 'qt.toolchain.cmake'}, and no "
                "[ios] deployment_target was set in pysidedeploy.spec. Set it explicitly."
            )
        elif qt_min_deployment_target is None:
            logging.warning(
                "[DEPLOY] Could not read Qt's minimum iOS deployment target from "
                f"qt.toolchain.cmake, so [ios] deployment_target = \"{deployment_target}\" "
                "could not be validated against it."
            )
        elif (_version_tuple(deployment_target, f"the iOS deployment target from {target_source}")
                < _version_tuple(qt_min_deployment_target,
                                 "Qt's minimum iOS deployment target")):
            raise RuntimeError(
                f"[DEPLOY] [ios] deployment_target = \"{deployment_target}\" is lower than "
                f"{qt_min_deployment_target}, the minimum iOS version this Qt kit's binaries "
                "were themselves built for -- the app would claim to support OS versions its "
                "own linked Qt libraries can't run on."
            )
        logging.info(f"[DEPLOY] iOS deployment target: {deployment_target} "
                     f"(from {target_source})")
        self.deployment_target = deployment_target

    @property
    def wheel_pyside(self) -> Path:
        return self._wheel_pyside

    @wheel_pyside.setter
    def wheel_pyside(self, wheel_pyside: Path):
        self._wheel_pyside = wheel_pyside.resolve() if wheel_pyside else None
        if self._wheel_pyside:
            self.set_value("ios", "wheel_pyside", str(self._wheel_pyside))

    @property
    def wheel_shiboken(self) -> Path:
        return self._wheel_shiboken

    @wheel_shiboken.setter
    def wheel_shiboken(self, wheel_shiboken: Path):
        self._wheel_shiboken = wheel_shiboken.resolve() if wheel_shiboken else None
        if self._wheel_shiboken:
            self.set_value("ios", "wheel_shiboken", str(self._wheel_shiboken))

    @property
    def xcframework_path(self) -> Path:
        return self._xcframework_path

    @xcframework_path.setter
    def xcframework_path(self, xcframework_path: Path):
        self._xcframework_path = xcframework_path.resolve() if xcframework_path else None
        if self._xcframework_path:
            self.set_value("ios", "xcframework_path", str(self._xcframework_path))

    @property
    def pyside6_dir(self) -> Path:
        """PySide6/ package directory, unpacked from wheel_pyside. Both the
        Qt module archives and libpyside6.a/libpyside6qml.a sit directly
        here, along with the full embedded Qt-for-iOS kit under Qt/."""
        return _unpack_wheel(self.wheel_pyside, self.generated_files_path / "_wheels", "PySide6")

    @property
    def shiboken_dir(self) -> Path:
        """shiboken6/ package directory, unpacked from wheel_shiboken.
        libshiboken6.a and Shiboken.a both sit directly here."""
        return _unpack_wheel(self.wheel_shiboken, self.generated_files_path / "_wheels",
                             "shiboken6")

    @property
    def qt_ios(self) -> Path:
        """The Qt-for-iOS kit is embedded inside the PySide6 wheel
        (frameworks, headers, .prl files, plugins, qml modules, qt.toolchain.cmake)"""
        return self.pyside6_dir / "Qt"

    @property
    def name(self) -> str:
        return self.title

    @property
    def project_root(self) -> Path:
        return self.project_dir

    @property
    def output_dir(self) -> Path:
        return self.generated_files_path

    @property
    def scripts(self) -> list[str]:
        """
        All local .py files to bundle -- main.py (source_file) always
        first, so main_mm.py's entry_script = cfg.scripts[0] still resolves
        correctly, followed by every other local .py file
        """
        main_rel = (str(self.source_file.relative_to(self.project_dir))
                    if self.source_file.is_relative_to(self.project_dir)
                    else str(self.source_file))
        others = sorted(
            str(f.relative_to(self.project_dir))
            for f in get_py_files(self.project_dir, extra_ignore_dirs=self.extra_ignore_dirs,
                                  project_data=self.project_data)
            if str(f.relative_to(self.project_dir)) != main_rel
        )
        return [main_rel] + others

    @property
    def qt_modules(self) -> list[str]:
        """cfg.modules with the 'Qt' prefix restored, eg: "Core" -> "QtCore"."""
        return [f"Qt{m}" for m in self.modules]

    @property
    def qml_dirs(self) -> list[str]:
        """App-local QML directories to bundle."""
        dirs = set()
        for f in self.qml_files:
            parent = f.parent.relative_to(self.project_dir) if f.is_relative_to(self.project_dir) \
                else f.parent
            if str(parent) != ".":
                dirs.add(str(parent))
        return sorted(dirs)

    @property
    def qml_qt_modules(self) -> list[str]:
        """QML import URIs used (eg "QtQuick.Controls"), for resolve_qml_plugins()."""
        self._find_qtquick_modules()
        return sorted(self.qml_modules)
