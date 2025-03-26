# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import shutil
import re
import os
import stat
import sys
import subprocess

from urllib import request
from pathlib import Path
from packaging import version
from tqdm import tqdm

# the tag number does not matter much since we update the sdk later
DEFAULT_SDK_TAG = 6514223
ANDROID_NDK_VERSION = "27c"
ANDROID_NDK_VERSION_NUMBER_SUFFIX = "12479018"


def run_command(command: list[str], cwd: str | None = None, ignore_fail: bool = False,
                dry_run: bool = False, accept_prompts: bool = False, show_stdout: bool = False,
                capture_stdout: bool = False):

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
                            capture_output=capture_stdout)

    if result.returncode != 0 and not ignore_fail:
        sys.exit(result.returncode)

    if capture_stdout and not result.returncode:
        return result.stdout.decode("utf-8")

    return None


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class SdkManager:
    def __init__(self, android_sdk_dir: Path, dry_run: bool = False):
        self._sdk_manager = android_sdk_dir / "tools" / "bin" / "sdkmanager"

        if not self._sdk_manager.exists():
            raise RuntimeError(f"Unable to find SdkManager in {str(self._sdk_manager)}")

        if not os.access(self._sdk_manager, os.X_OK):
            current_permissions = stat.S_IMODE(os.lstat(self._sdk_manager).st_mode)
            os.chmod(self._sdk_manager, current_permissions | stat.S_IEXEC)

        self._android_sdk_dir = android_sdk_dir
        self._dry_run = dry_run

    def list_packages(self):
        command = [self._sdk_manager, f"--sdk_root={self._android_sdk_dir}", "--list"]
        return run_command(command=command, dry_run=self._dry_run, show_stdout=True,
                           capture_stdout=True)

    def install(self, *args, accept_license: bool = False, show_stdout=False):
        command = [str(self._sdk_manager), f"--sdk_root={self._android_sdk_dir}", *args]
        run_command(command=command, dry_run=self._dry_run,
                    accept_prompts=accept_license, show_stdout=show_stdout)


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


def extract_dmg(file: Path, destination: Path):
    output = run_command(['hdiutil', 'attach', '-nobrowse', '-readonly', str(file)],
                         show_stdout=True, capture_stdout=True)

    # find the mounted volume
    result = re.search(r'/Volumes/(.*)', output)
    if not result:
        raise RuntimeError(f"Unable to find mounted volume for file {file}")
    mounted_vol_name = result.group(1)
    if not mounted_vol_name:
        raise RuntimeError(f"Unable to find mounted volume for file {file}")

    # copy files
    shutil.copytree(f'/Volumes/{mounted_vol_name}/', destination, dirs_exist_ok=True)

    # Detach mounted volume
    run_command(['hdiutil', 'detach', f'/Volumes/{mounted_vol_name}'])


def _download(url: str, destination: Path):
    """
    Download url to destination
    """
    headers, download_path = None, None
    # https://github.com/tqdm/tqdm#hooks-and-callbacks
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        download_path, headers = request.urlretrieve(url=url, filename=destination,
                                                     reporthook=t.update_to)
    assert Path(download_path).resolve() == destination


def download_android_ndk(ndk_path: Path):
    """
    Downloads the given ndk_version into ndk_path
    """
    ndk_path = ndk_path / "android-ndk"
    ndk_extension = "dmg" if sys.platform == "darwin" else "zip"
    ndk_zip_path = ndk_path / f"android-ndk-r{ANDROID_NDK_VERSION}-{sys.platform}.{ndk_extension}"
    ndk_version_path = ""
    if sys.platform == "linux":
        ndk_version_path = ndk_path / f"android-ndk-r{ANDROID_NDK_VERSION}"
    elif sys.platform == "darwin":
        ndk_version_path = (ndk_path
                            / f"AndroidNDK{ANDROID_NDK_VERSION_NUMBER_SUFFIX}.app/Contents/NDK")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    if ndk_version_path.exists():
        print(f"NDK path found in {str(ndk_version_path)}")
    else:
        try:
            ndk_path.mkdir(parents=True, exist_ok=True)
            url = (f"https://dl.google.com/android/repository"
                   f"/android-ndk-r{ANDROID_NDK_VERSION}-{sys.platform}.{ndk_extension}")

            print(f"Downloading Android Ndk version r{ANDROID_NDK_VERSION}")
            _download(url=url, destination=ndk_zip_path)

            print("Unpacking Android Ndk")
            if sys.platform == "darwin":
                extract_dmg(file=ndk_zip_path, destination=ndk_path)
            else:
                extract_zip(file=ndk_zip_path, destination=ndk_path)
        except Exception as e:
            print(f"Error occurred while downloading and unpacking Android NDK: {e}")
            if ndk_path.exists():
                shutil.rmtree(ndk_path)
            sys.exit(1)

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
    cltools_path = android_sdk_dir / "tools"

    if cltools_path.exists():
        print(f"Command-line tools found in {str(cltools_path)}")
    else:
        try:
            android_sdk_dir.mkdir(parents=True, exist_ok=True)

            print("Download Android Command Line Tools: "
                  f"commandlinetools-{sys.platform}-{DEFAULT_SDK_TAG}_latest.zip")
            _download(url=url, destination=cltools_zip_path)

            print("Unpacking Android Command Line Tools")
            extract_zip(file=cltools_zip_path, destination=android_sdk_dir)
        except Exception as e:
            print(f"Error occurred while downloading and unpacking Android Command Line Tools: {e}")
            if android_sdk_dir.exists():
                shutil.rmtree(android_sdk_dir)
            sys.exit(1)

    return android_sdk_dir


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
    tools_dir = android_sdk_dir / "tools"
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
