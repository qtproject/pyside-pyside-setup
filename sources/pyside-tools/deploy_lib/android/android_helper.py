# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
import os
import subprocess
import sys
import logging
import zipfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from jinja2 import Environment, FileSystemLoader

from .. import run_command
from .android_utilities import SUPPORTED_ANDROID_PLATFORMS

# The only Jdk major version python-for-android accepts. See
# JDKPrerequisite in pythonforandroid/prerequisites.py.
P4A_REQUIRED_JDK_VERSION = 17


@dataclass
class AndroidData:
    """
    Dataclass to store all the Android data obtained through cli
    """
    wheel_pyside: Path
    wheel_shiboken: Path
    ndk_path: Path
    sdk_path: Path


def create_recipe(version: str, component: str, wheel_path: str, generated_files_path: Path,
                  qt_modules: list[str] = None, local_libs: list[str] = None,
                  plugins: list[str] = None):
    '''
    Create python_for_android recipe for PySide6 and shiboken6
    '''
    qt_plugins = []
    if plugins:
        # split plugins based on category
        for plugin in plugins:
            plugin_category, plugin_name = plugin.split('_', 1)
            qt_plugins.append((plugin_category, plugin_name))

    qt_local_libs = []
    if local_libs:
        qt_local_libs = [local_lib for local_lib in local_libs if local_lib.startswith("Qt6")]

    rcp_tmpl_path = Path(__file__).parent / "recipes" / f"{component}"
    environment = Environment(loader=FileSystemLoader(rcp_tmpl_path))
    template = environment.get_template("__init__.tmpl.py")
    content = template.render(
        version=version,
        wheel_path=wheel_path,
        qt_modules=qt_modules,
        qt_local_libs=qt_local_libs,
        qt_plugins=qt_plugins
    )

    recipe_path = generated_files_path / "recipes" / f"{component}"
    recipe_path.mkdir(parents=True, exist_ok=True)
    logging.info(f"[DEPLOY] Writing {component} recipe into {str(recipe_path)}")
    with open(recipe_path / "__init__.py", mode="w", encoding="utf-8") as recipe:
        recipe.write(content)


def safe_extractall(archive: ZipFile, target_path: Path) -> None:
    """
    Extract all members of a zip archive into target_path, checking that each entry
    resolves inside target_path to prevent path traversal attacks.
    """
    resolved_target = target_path.resolve()
    for member in archive.infolist():
        member_path = (target_path / member.filename).resolve()
        if not member_path.is_relative_to(resolved_target):
            raise RuntimeError(
                f"[DEPLOY] Refusing to extract '{member.filename}': "
                f"path resolves outside the extraction directory"
            )
        archive.extract(member, target_path)


def extract_and_copy_jar(wheel_path: Path, generated_files_path: Path) -> str:
    '''
    extracts the PySide6 wheel and copies the 'jar' folder to 'generated_files_path'.
    These .jar files are added to the buildozer.spec file to be used later by buildozer
    '''
    jar_path = generated_files_path / "jar"
    jar_path.mkdir(parents=True, exist_ok=True)
    archive = ZipFile(wheel_path)
    jar_files = [file for file in archive.namelist() if file.startswith("PySide6/jar")]
    for file in jar_files:
        archive.extract(file, jar_path)
    return (jar_path / "PySide6" / "jar").resolve() if jar_files else None


def get_wheel_android_arch(wheel: Path):
    '''
    Get android architecture from wheel
    '''
    supported_archs = SUPPORTED_ANDROID_PLATFORMS
    for arch in supported_archs:
        if arch in wheel.stem:
            return arch

    return None


def get_llvm_readobj(ndk_path: Path) -> Path:
    '''
    Return the path to llvm_readobj from the Android Ndk
    '''
    # TODO: Requires change if Windows platform supports Android Deployment or if we
    # support host other than linux-x86_64
    return (ndk_path / f"toolchains/llvm/prebuilt/{sys.platform}-x86_64/bin/llvm-readobj")


def check_jdk_version() -> None:
    """
    Fail early if the Jdk is not the one python-for-android requires.

    p4a accepts exactly one Jdk major version and checks it on every run,
    including 'p4a aab -h', which buildozer calls to probe for features.
    When the check fails p4a asks whether to install a Jdk itself, and
    buildozer hides that prompt, so the build stops with no output until
    the question is answered. Report it here instead.

    Only enforced on macOS, where p4a treats the Jdk as mandatory.
    """
    if sys.platform != "darwin":
        return

    # Resolve the same Jdk p4a would, see JDKPrerequisite.darwin_checker().
    jdk_path = os.environ.get("JAVA_HOME")
    if jdk_path:
        logging.info(f"[DEPLOY] Checking the Jdk from JAVA_HOME: {jdk_path}")
    else:
        jdk_path = subprocess.run(["/usr/libexec/java_home"], capture_output=True,
                                  text=True).stdout.strip()

    major_version = None
    javac = Path(jdk_path) / "bin" / "javac" if jdk_path else None
    if javac and javac.exists():
        # Older javac reports the version on stderr, newer ones on stdout.
        result = subprocess.run([str(javac), "-version"], capture_output=True, text=True)
        version_output = (result.stdout or result.stderr).strip()
        try:
            major_version = int(version_output.split(" ")[-1].split(".")[0])
        except (IndexError, ValueError):
            logging.warning(f"[DEPLOY] Unable to read the Jdk version from '{version_output}'")

    if major_version == P4A_REQUIRED_JDK_VERSION:
        return

    found = f"Jdk {major_version}" if major_version else "no usable Jdk"
    raise RuntimeError(
        f"[DEPLOY] python-for-android requires Jdk {P4A_REQUIRED_JDK_VERSION}, but "
        f"{found} was found at '{jdk_path or 'no path'}'. Install Jdk "
        f"{P4A_REQUIRED_JDK_VERSION} and point JAVA_HOME at it, for example:\n"
        f"    export JAVA_HOME=$(/usr/libexec/java_home -v {P4A_REQUIRED_JDK_VERSION})\n"
        "Without it the build stops without printing a reason, because "
        "python-for-android waits for an answer to a prompt that buildozer hides."
    )


def ensure_legacy_sdk_tools_path(sdk_path: Path) -> None:
    """
    Expose the Sdk command line tools where buildozer and p4a look.

    Current builds unpack to <sdk>/cmdline-tools, but buildozer and p4a
    expect the tools in <sdk>/tools/bin. This creates a symlink to bridge
    the gap. See https://github.com/kivy/buildozer/pull/1511
    """
    legacy_tools_dir = sdk_path / "tools"
    cmdline_tools_dir = sdk_path / "cmdline-tools"

    if legacy_tools_dir.exists() or legacy_tools_dir.is_symlink():
        return

    if not (cmdline_tools_dir / "bin" / "sdkmanager").exists():
        return

    logging.info(f"[DEPLOY] Linking {legacy_tools_dir} to {cmdline_tools_dir}, because buildozer "
                 "and python-for-android look for the Sdk command line tools in the old SDK "
                 "Tools location")
    legacy_tools_dir.mkdir()
    for entry in ("bin", "lib"):
        (legacy_tools_dir / entry).symlink_to(cmdline_tools_dir / entry,
                                              target_is_directory=True)


def find_lib_dependencies(llvm_readobj: Path, lib_path: Path, used_dependencies: set[str] = None,
                          dry_run: bool = False):
    """
    Find all the Qt dependencies of a library using llvm_readobj
    """
    if lib_path.name in used_dependencies:
        return

    used_dependencies.add(lib_path.name)

    command = [str(llvm_readobj), "--needed-libs", str(lib_path)]

    # even if dry_run is given, we need to run the actual command to see all the dependencies
    # for which llvm-readelf is run.
    if dry_run:
        _, output = run_command(command=command, dry_run=dry_run, fetch_output=True)
    _, output = run_command(command=command, dry_run=False, fetch_output=True)

    dependencies = set()
    neededlibraries_found = False
    for line in output.splitlines():
        line = line.decode("utf-8").lstrip()
        if line.startswith("NeededLibraries") and not neededlibraries_found:
            neededlibraries_found = True
        if neededlibraries_found and line.startswith("libQt"):
            dependencies.add(line)
            used_dependencies.add(line)
            dependent_lib_path = lib_path.parent / line
            find_lib_dependencies(llvm_readobj, dependent_lib_path, used_dependencies, dry_run)

    if dependencies:
        logging.info(f"[DEPLOY] Following dependencies found for {lib_path.stem}: {dependencies}")
    else:
        logging.info(f"[DEPLOY] No Qt dependencies found for {lib_path.stem}")


def find_qtlibs_in_wheel(wheel_pyside: Path):
    """
    Find the path to Qt/lib folder inside the wheel.
    """
    archive = ZipFile(wheel_pyside)
    qt_libs_path = wheel_pyside / "PySide6/Qt/lib"
    qt_libs_path = zipfile.Path(archive, at=qt_libs_path)
    if not qt_libs_path.exists():
        for file in archive.namelist():
            # the dependency files are inside the libs folder
            if file.endswith("android-dependencies.xml"):
                qt_libs_path = zipfile.Path(archive, at=file).parent
                # all dependency files are in the same path
                break

    if not qt_libs_path:
        raise FileNotFoundError("[DEPLOY] Unable to find Qt libs folder inside the wheel")

    return qt_libs_path
