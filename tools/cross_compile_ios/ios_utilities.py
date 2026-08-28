# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import hashlib
import logging
import re
import shutil
import ssl
import tarfile
import urllib.error
import sys
import urllib.request
from tqdm import tqdm
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PYSIDE_SETUP_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PYSIDE_SETUP_ROOT))
from build_scripts.utils import (configure_cmake_project,           # noqa: E402
                                 parse_cmake_project_message_info)

try:
    import certifi
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except ImportError:
    pass


PYTHON_VERSION = "3.15"       # major.minor -- used for stdlib paths (lib/pythonX.Y)
PYTHON_RELEASE = "3.15.0rc1"  # exact python.org release tag for the iOS XCframework

TEMPLATES_PATH = Path(__file__).parent / "templates"
IOS_CACHE_DIR = Path.home() / ".pyside6_ios"

DEFAULT_QT_CMAKEDIR = "lib/cmake"
TARGET_QT_INFO_DIR = PYSIDE_SETUP_ROOT / "sources" / "shiboken6" / "config.tests" / "target_qt_info"


PYTHON_ORG_IOS_URL = (
    "https://www.python.org/ftp/python/{base_version}/python-{release}-iOS-XCframework.tar.gz"
)

# published directly on the python.org release page
_PYTHON_IOS_SHA256: dict[str, str] = {
    "3.15.0rc1": "178bf7bef9cd0f18b27cacb98b14332a5ba44c9427543ffb71f8809bc1f11c3c",
}


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def _verify_sha256(file_path: Path, expected: str) -> None:
    h = hashlib.sha256()
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"Checksum mismatch for '{file_path.name}': "
            f"expected {expected}, got {actual}"
        )


def download_python_support(
    release: str = PYTHON_RELEASE,
    cache_dir: Path = IOS_CACHE_DIR / "Python-iOS",
) -> Path:

    base_version = re.match(r"^\d+\.\d+\.\d+", release).group()
    archive_name = f"python-{release}-iOS-XCframework.tar.gz"
    archive_path = cache_dir / archive_name
    extract_dir = cache_dir / release

    url = PYTHON_ORG_IOS_URL.format(base_version=base_version, release=release)
    expected_sha256 = _PYTHON_IOS_SHA256.get(release)

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        logging.info(f"Using cached archive: {archive_path}")
        _verify_sha256(archive_path, expected_sha256)
    else:
        logging.info(f"Downloading {url} -> {archive_path}")
        try:
            with DownloadProgressBar(unit="B",
                                     unit_scale=True,
                                     miniters=1,
                                     desc=archive_path.name) as bar:
                urllib.request.urlretrieve(url,
                                           archive_path,
                                           reporthook=bar.update_to)
            _verify_sha256(archive_path, expected_sha256)
        except (urllib.error.URLError, OSError, RuntimeError) as e:
            archive_path.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download {url}: {e}") from e
        logging.info(f"Download complete: {archive_path}")

    if extract_dir.exists():
        logging.info(f"Using cached extraction: {extract_dir}")
    else:
        logging.info(f"Extracting {archive_path} -> {extract_dir}")
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(archive_path) as tf:
                tf.extractall(extract_dir, filter='data')
        except (tarfile.TarError, OSError) as e:
            shutil.rmtree(extract_dir, ignore_errors=True)
            raise RuntimeError(f"Failed to extract {archive_path}: {e}") from e
        logging.info(f"Extraction complete: {extract_dir}")

    return extract_dir / "Python.xcframework"


def _query_qt_install_cmakedir(
        qt_ios: Path,
        cmake: str = "cmake",
) -> str | None:
    """Query Qt's QT_INSTALL_CMAKEDIR via the target_qt_info config.tests,
    instead of assuming the default 'lib/cmake'."""
    cmake_cache_args = [
        ("QFP_QT_TARGET_PATH", qt_ios),
        ("CMAKE_SYSTEM_NAME", "iOS"),
    ]
    output = configure_cmake_project(
        TARGET_QT_INFO_DIR, cmake,
        temp_prefix_build_path=IOS_CACHE_DIR / "config.tests",
        cmake_cache_args=cmake_cache_args)
    return parse_cmake_project_message_info(output)["qt_info"]["QT_INSTALL_CMAKEDIR"] or None


def python_xcframework_slice_dir(arch: str, simulator: bool) -> str:
    """The simulator slice is always a single merged 'ios-arm64_x86_64-simulator'"""
    return "ios-arm64_x86_64-simulator" if simulator else f"ios-{arch}"


def generate_toolchain(
        arch: str,
        simulator: bool,
        python_xcframework: Path,
        qt_ios: Path,
) -> Path:

    try:
        qt_install_prefix_cmakedir = _query_qt_install_cmakedir(qt_ios)
    except (RuntimeError, OSError) as e:
        logging.warning(
            f"Failed to find Qt's cmake dir; "
            f"falling back to '{DEFAULT_QT_CMAKEDIR}'.\n{e}"
        )
        qt_install_prefix_cmakedir = None
    qt_cmake_dir = qt_install_prefix_cmakedir or f"{qt_ios}/{DEFAULT_QT_CMAKEDIR}"

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_PATH)))
    template = env.get_template("toolchain_ios.tmpl.cmake")

    content = template.render(
        arch=arch,
        simulator=simulator,
        python_xcframework=str(python_xcframework),
        python_slice_dir=python_xcframework_slice_dir(arch, simulator),
        python_version=PYTHON_VERSION,
        host_python=sys.executable,
        qt_cmake_dir=qt_cmake_dir,
    )

    suffix = f"{arch}_simulator" if simulator else arch
    toolchain_path = IOS_CACHE_DIR / f"toolchain_ios_{suffix}.cmake"
    IOS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    toolchain_path.write_text(content)
    logging.info(f"Toolchain written: {toolchain_path}")
    return toolchain_path
