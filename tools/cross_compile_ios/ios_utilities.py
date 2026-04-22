# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import hashlib
import logging
import shutil
import ssl
import tarfile
import urllib.error
import urllib.request
from tqdm import tqdm
from pathlib import Path

try:
    import certifi
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except ImportError:
    pass


PYTHON_VERSION = "3.14"
BUILD_NUMBER = "b9"    # Latest

CACHE_DIR = Path.home() / ".pyside6_ios" / "Python-Apple-support"


BEEWARE_RELEASE_URL = (
    "https://github.com/beeware/Python-Apple-support/releases/download"
    "/{tag}/Python-{python_version}-iOS-support.{build}.tar.gz"
)

# beeware does not publish official checksums, so this is SHA-256 sum
# computed from that specific file
_PYTHON_SUPPORT_SHA256: dict[str, str] = {
    "3.14-b9": "8e4123b543bf17fdae2e2c6c033434487752438431014eb12e6d833aa35927a8",
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
    python_version: str = PYTHON_VERSION,
    build_number: str = BUILD_NUMBER,
    cache_dir: Path = CACHE_DIR,
) -> Path:

    tag = f"{python_version}-{build_number}"
    archive_name = f"Python-{python_version}-iOS-support.{build_number}.tar.gz"
    archive_path = cache_dir / archive_name
    extract_dir = cache_dir / tag

    url = BEEWARE_RELEASE_URL.format(
        tag=tag, python_version=python_version, build=build_number
    )

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        logging.info(f"Using cached archive: {archive_path}")
        _verify_sha256(archive_path, _PYTHON_SUPPORT_SHA256.get(tag))
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
            _verify_sha256(archive_path, _PYTHON_SUPPORT_SHA256.get(tag))
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
