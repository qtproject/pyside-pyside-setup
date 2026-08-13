# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:critical reason:execute-external-code,handling-untrusted-data
from __future__ import annotations

import hashlib
import logging
import shutil
import os
import stat
import sys
import subprocess
import tarfile

from urllib import request
from pathlib import Path
from packaging import version
from tqdm import tqdm

# the tag number does not matter much since we update the sdk later
DEFAULT_SDK_TAG = 14742923
# r28c is the first NDK whose Clang defaults to 16 KB page-aligned LOAD
# segments, which recent Android versions require. Everything p4a builds
# itself (libpython, libsqlite3, libssl, libffi) picks up that default;
# those come from p4a's own autotools recipes, which we cannot pass
# linker flags to. Note Qt documents r27c for its own Android libraries.
ANDROID_NDK_VERSION = "28c"

# CPython supports only these two Android ABIs. See HOSTS in CPython's
# Android/android.py. 32-bit Android is not a supported CPython target.
SUPPORTED_ANDROID_PLATFORMS = ["aarch64", "x86_64"]

# Android target Python. python.org ships official prebuilt Android
# binaries from 3.14 onwards, so CPython is no longer built here. This
# must match the python3 recipe version at the python-for-android commit
# pinned by P4A_COMMIT in deploy_lib/android/buildozer.py, because that
# is the interpreter which loads these wheels on the device.
ANDROID_TARGET_PYTHON_VERSION = "3.14"
ANDROID_TARGET_PYTHON_FULL_VERSION = "3.14.2"

# Minimum Android API level, set by Qt's requirements. Update when Qt's
# minimum API level changes.
MIN_ANDROID_API_LEVEL = "28"

# API level Qt for Python is compiled against. Higher than Qt's runtime
# minimum for toolchain compatibility, while staying compatible with it.
DEFAULT_ANDROID_API_LEVEL = "35"

# Official SHA-1 checksums for the pinned NDK/SDK versions, taken from
# dl.google.com/android/repository/repository2-3.xml. The NDK entry is
# ndk;28.2.13676358 (r28c).
_NDK_SHA1: dict[str, str] = {
    "linux": "a7b54a5de87fecd125a17d54f73c446199e72a64",
    "darwin": "fc20a6bf15a30fb3428c9b60a7308793a362dc6d",
}
_CLTOOLS_SHA1: dict[str, str] = {
    "linux": "48833c34b761c10cb20bcd16582129395d121b27",
    "mac": "cc27cca4b84bfdbc7df17e3d0a01d0c640d8ee71",
}

# Official SHA-256 checksums for the pinned prebuilt Python tarballs.
# Update together with ANDROID_TARGET_PYTHON_FULL_VERSION.
_PREBUILT_PYTHON_SHA256: dict[str, str] = {
    "aarch64": "d842ed92a662e41f8008ad2ec6b0cb36e5872c64f073f5abfce7f8279a1c761c",
    "x86_64": "622415c0e241fc75bf32ee87f3e0b4fd96044a372c156021191a76e651c1bef4",
}


def _verify_checksum(file_path: Path, expected: str,
                     algorithm: str = "sha1") -> None:
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"[DEPLOY] Checksum mismatch for '{file_path.name}': "
            f"expected {expected}, got {actual}"
        )


def run_command(command: list[str], cwd: str | None = None, ignore_fail: bool = False,
                dry_run: bool = False, accept_prompts: bool = False, show_stdout: bool = False,
                capture_stdout: bool = False, env: dict | None = None):

    if capture_stdout and not show_stdout:
        raise RuntimeError("capture_stdout should always be used together with show_stdout")

    if dry_run:
        print(" ".join(command))
        return

    input = None
    if accept_prompts:
        input = str.encode("y")

    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.DEVNULL

    result = subprocess.run(command, cwd=cwd, input=input, stdout=stdout,
                            capture_output=capture_stdout, env=env)

    if result.returncode != 0 and not ignore_fail:
        sys.exit(result.returncode)

    if capture_stdout and not result.returncode:
        return result.stdout.decode("utf-8")

    return None


def _find_java_home() -> str | None:
    # Prefer an explicit JAVA_HOME already set in the environment.
    java_home = os.environ.get("JAVA_HOME")
    if java_home and Path(java_home).exists():
        return java_home

    # macOS ships /usr/libexec/java_home
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["/usr/libexec/java_home"], capture_output=True, text=True
            )
            if result.returncode == 0:
                candidate = result.stdout.strip()
                if candidate and Path(candidate).exists():
                    return candidate
        except FileNotFoundError:
            pass

    # Common Homebrew JDK install paths
    for candidate in ["/opt/homebrew/opt/openjdk", "/usr/local/opt/openjdk"]:
        if Path(candidate).exists():
            return candidate

    return None


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class SdkManager:
    def __init__(self, android_sdk_dir: Path, dry_run: bool = False):
        self._sdk_manager = android_sdk_dir / "cmdline-tools" / "bin" / "sdkmanager"

        if not self._sdk_manager.exists():
            raise RuntimeError(f"Unable to find SdkManager in {str(self._sdk_manager)}")

        if not os.access(self._sdk_manager, os.X_OK):
            current_permissions = stat.S_IMODE(os.lstat(self._sdk_manager).st_mode)
            os.chmod(self._sdk_manager, current_permissions | stat.S_IEXEC)

        self._android_sdk_dir = android_sdk_dir
        self._dry_run = dry_run

        # sdkmanager is a JVM tool
        # ensure JAVA_HOME is set so it can find the runtime.
        self._env = dict(os.environ)
        java_home = _find_java_home()
        if java_home:
            self._env["JAVA_HOME"] = java_home
            logging.info(f"Using Java from: {java_home}")
        else:
            raise RuntimeError(
                "Java Runtime not found. sdkmanager requires a JDK to run.\n"
                "Install one with:\n"
                "  brew install --cask temurin\n"
                "or set the JAVA_HOME environment variable to your JDK installation."
            )

    def list_packages(self):
        command = [self._sdk_manager, f"--sdk_root={self._android_sdk_dir}", "--list"]
        return run_command(command=command, dry_run=self._dry_run, show_stdout=True,
                           capture_stdout=True, env=self._env)

    def install(self, *args, accept_license: bool = False, show_stdout=False):
        command = [str(self._sdk_manager), f"--sdk_root={self._android_sdk_dir}", *args]
        run_command(command=command, dry_run=self._dry_run,
                    accept_prompts=accept_license, show_stdout=show_stdout, env=self._env)


def extract_zip(file: Path, destination: Path):
    """
    Unpacks the zip file into destination preserving all permissions

    TODO: Try to use zipfile module. Currently we cannot use zipfile module here because
    extractAll() does not preserve permissions.

    In case `unzip` is not available, the user is requested to install it manually
    """
    unzip = shutil.which("unzip")
    if not unzip:
        raise RuntimeError("Unable to find program unzip. Use `sudo apt-get install unzip`"
                           "to install it")

    command = [unzip, str(file), "-d", str(destination)]
    run_command(command=command, show_stdout=True)


def _download(url: str, destination: Path):
    """
    Download url to destination
    """
    headers, download_path = None, None
    # https://github.com/tqdm/tqdm#hooks-and-callbacks
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        download_path, headers = request.urlretrieve(url=url, filename=destination,
                                                     reporthook=t.update_to)
    if Path(download_path).resolve() != destination:
        raise RuntimeError(
            f"[DEPLOY] Downloaded file path '{download_path}' does not match "
            f"expected destination '{destination}'"
        )


def download_android_ndk(ndk_path: Path):
    """
    Downloads the given ndk_version into ndk_path
    """
    if sys.platform not in ("linux", "darwin"):
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    ndk_path = ndk_path / "android-ndk"
    # Since r28c, the macOS NDK is a plain zip unpacking to a flat
    # android-ndk-r<version>/ directory, same as Linux. Earlier versions
    # shipped a .dmg holding an AndroidNDK<build>.app bundle instead.
    ndk_zip_path = ndk_path / f"android-ndk-r{ANDROID_NDK_VERSION}-{sys.platform}.zip"
    ndk_version_path = ndk_path / f"android-ndk-r{ANDROID_NDK_VERSION}"

    if ndk_version_path.exists():
        print(f"NDK path found in {str(ndk_version_path)}")
    else:
        try:
            ndk_path.mkdir(parents=True, exist_ok=True)
            url = (f"https://dl.google.com/android/repository"
                   f"/android-ndk-r{ANDROID_NDK_VERSION}-{sys.platform}.zip")

            print(f"Downloading Android Ndk version r{ANDROID_NDK_VERSION}")
            _download(url=url, destination=ndk_zip_path)
            _verify_checksum(ndk_zip_path, _NDK_SHA1[sys.platform])

            print("Unpacking Android Ndk")
            extract_zip(file=ndk_zip_path, destination=ndk_path)
        except Exception as e:
            print(f"Error occurred while downloading and unpacking Android NDK: {e}")
            if ndk_path.exists():
                shutil.rmtree(ndk_path)
            sys.exit(1)

    # strip Gatekeeper quarantine on every macOS invocation of the NDK, since it contains
    # executables that may be blocked from running until the quarantine is removed.
    if sys.platform == "darwin" and ndk_version_path.exists():
        run_command(['xattr', '-cr', str(ndk_version_path)], ignore_fail=True)

    return ndk_version_path


def download_android_commandlinetools(android_sdk_dir: Path):
    """
    Downloads Android commandline tools into cltools_path.
    """
    sdk_platform = sys.platform if sys.platform != "darwin" else "mac"
    android_sdk_dir = android_sdk_dir / "android-sdk"
    url = ("https://dl.google.com/android/repository/"
           f"commandlinetools-{sdk_platform}-{DEFAULT_SDK_TAG}_latest.zip")
    cltools_zip_path = (android_sdk_dir
                        / f"commandlinetools-{sdk_platform}-{DEFAULT_SDK_TAG}_latest.zip")
    cltools_path = android_sdk_dir / "cmdline-tools"

    if cltools_path.exists():
        print(f"Command-line tools found in {str(cltools_path)}")
    else:
        try:
            android_sdk_dir.mkdir(parents=True, exist_ok=True)

            print("Download Android Command Line Tools: "
                  f"commandlinetools-{sys.platform}-{DEFAULT_SDK_TAG}_latest.zip")
            _download(url=url, destination=cltools_zip_path)
            _verify_checksum(cltools_zip_path, _CLTOOLS_SHA1[sdk_platform])

            print("Unpacking Android Command Line Tools")
            extract_zip(file=cltools_zip_path, destination=android_sdk_dir)
        except Exception as e:
            print(f"Error occurred while downloading and unpacking Android Command Line Tools: {e}")
            if android_sdk_dir.exists():
                shutil.rmtree(android_sdk_dir)
            sys.exit(1)

    return android_sdk_dir


def download_prebuilt_python_android(full_version: str, plat_name: str,
                                     install_path: Path) -> None:
    """
    Downloads the official prebuilt CPython for Android from python.org,
    verifies it and extracts it into install_path.

    The tarball contains a top-level 'prefix/' directory holding the
    include/ and lib/ layout the CMake toolchain file expects, so its
    contents are extracted with that prefix stripped.
    """
    expected_sha256 = _PREBUILT_PYTHON_SHA256.get(plat_name)
    if expected_sha256 is None:
        raise RuntimeError(
            f"[DEPLOY] No prebuilt Python checksum for platform "
            f"'{plat_name}'. Supported: "
            f"{sorted(_PREBUILT_PYTHON_SHA256)}")

    archive_name = f"python-{full_version}-{plat_name}-linux-android.tar.gz"
    url = f"https://www.python.org/ftp/python/{full_version}/{archive_name}"

    install_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path = install_path.parent / archive_name

    if not archive_path.exists():
        logging.info(f"Downloading prebuilt Python {full_version} for "
                     f"{plat_name}")
        _download(url, archive_path)
    else:
        logging.info(f"Using cached prebuilt Python: {archive_path}")

    _verify_checksum(archive_path, expected_sha256, algorithm="sha256")

    install_path.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path) as tar:
        members = []
        for member in tar.getmembers():
            name = member.name.removeprefix("./")
            if not name.startswith("prefix/"):
                continue
            member.name = name[len("prefix/"):]
            if not member.name:
                continue
            members.append(member)
        if not members:
            raise RuntimeError(f"{archive_name} has no prefix/ directory")
        tar.extractall(path=install_path, members=members, filter="data")


def android_list_build_tools_versions(sdk_manager: SdkManager):
    """
    List all the build-tools versions available for download
    """
    available_packages = sdk_manager.list_packages()
    build_tools_versions = []
    lines = available_packages.split('\n')

    for line in lines:
        if not line.strip().startswith('build-tools;'):
            continue
        package_name = line.strip().split(' ')[0]
        if package_name.count(';') != 1:
            raise RuntimeError(f"Unable to parse build-tools version: {package_name}")
        ver = package_name.split(';')[1]

        build_tools_versions.append(version.Version(ver))

    return build_tools_versions


def find_installed_buildtools_version(build_tools_dir: Path):
    """
    It is possible that the user has multiple build-tools installed. The newer  version is generally
    used. This function find the newest among the installed build-tools
    """
    versions = [version.Version(bt_dir.name) for bt_dir in build_tools_dir.iterdir()
                if bt_dir.is_dir()]
    return max(versions)


def find_latest_buildtools_version(sdk_manager: SdkManager):
    """
    Uses sdk manager to find the latest build-tools version
    """
    available_build_tools_v = android_list_build_tools_versions(sdk_manager=sdk_manager)

    if not available_build_tools_v:
        raise RuntimeError('Unable to find any build tools available for download')

    # find the latest build tools version that is not a release candidate
    # release candidates end has rc in the version number
    available_build_tools_v = [v for v in available_build_tools_v if "rc" not in str(v)]

    return max(available_build_tools_v)


def install_android_packages(android_sdk_dir: Path, android_api: str, dry_run: bool = False,
                             accept_license: bool = False, skip_update: bool = False):
    """
    Use the sdk manager to install build-tools, platform-tools and platform API
    """
    tools_dir = android_sdk_dir / "cmdline-tools"
    if not tools_dir.exists():
        raise RuntimeError("Unable to find Android command-line tools in "
                           f"{str(tools_dir)}")

    # incase of --verbose flag
    show_output = (logging.getLogger().getEffectiveLevel() == logging.INFO)

    sdk_manager = SdkManager(android_sdk_dir=android_sdk_dir, dry_run=dry_run)

    # install/upgrade platform-tools
    if not (android_sdk_dir / "platform-tools").exists():
        print("Installing/Updating Android platform-tools")
        sdk_manager.install("platform-tools", accept_license=accept_license,
                            show_stdout=show_output)
        # The --update command is only relevant for platform tools
        if not skip_update:
            sdk_manager.install("--update", show_stdout=show_output)

    # install/upgrade build-tools
    buildtools_dir = android_sdk_dir / "build-tools"

    if not buildtools_dir.exists():
        latest_build_tools_v = find_latest_buildtools_version(sdk_manager=sdk_manager)
        print(f"Installing Android build-tools version {latest_build_tools_v}")
        sdk_manager.install(f"build-tools;{latest_build_tools_v}", show_stdout=show_output)
    else:
        if not skip_update:
            latest_build_tools_v = find_latest_buildtools_version(sdk_manager=sdk_manager)
            installed_build_tools_v = find_installed_buildtools_version(buildtools_dir)
            if latest_build_tools_v > installed_build_tools_v:
                print(f"Updating Android build-tools version to {latest_build_tools_v}")
                sdk_manager.install(f"build-tools;{latest_build_tools_v}", show_stdout=show_output)
                installed_build_tools_v = latest_build_tools_v

    # install the platform API
    platform_api_dir = android_sdk_dir / "platforms" / f"android-{android_api}"
    if not platform_api_dir.exists():
        print(f"Installing Android platform API {android_api}")
        sdk_manager.install(f"platforms;android-{android_api}", show_stdout=show_output)

    print("Android packages installation done")
