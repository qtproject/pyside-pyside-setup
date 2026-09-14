# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:critical reason:handling-untrusted-data

import hashlib
import logging
import re
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


PYTHON_VERSION = "3.15"       # major.minor -- used for stdlib paths (lib/pythonX.Y)
PYTHON_RELEASE = "3.15.0rc2"  # exact python.org release tag for the iOS XCframework

TEMPLATES_PATH = Path(__file__).parent / "templates"
IOS_CACHE_DIR = Path.home() / ".pyside6_ios"

PYTHON_ORG_IOS_URL = (
    "https://www.python.org/ftp/python/{base_version}/python-{release}-iOS-XCframework.tar.gz"
)

# published directly on the python.org release page
_PYTHON_IOS_SHA256: dict[str, str] = {
    "3.15.0rc2": "2496d92689da625cd349e856e17b3d540787f8d17806e21536e8d394d940adc0",
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
    dry_run: bool = False,
) -> Path:

    base_version = re.match(r"^\d+\.\d+\.\d+", release).group()
    archive_name = f"python-{release}-iOS-XCframework.tar.gz"
    archive_path = cache_dir / archive_name
    extract_dir = cache_dir / release

    url = PYTHON_ORG_IOS_URL.format(base_version=base_version, release=release)
    expected_sha256 = _PYTHON_IOS_SHA256.get(release)

    if archive_path.exists():
        logging.info(f"Using cached archive: {archive_path}")
        _verify_sha256(archive_path, expected_sha256)
    elif dry_run:
        print(f"download {url} -> {archive_path}")
    else:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
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
    elif dry_run:
        print(f"extract {archive_path} -> {extract_dir}")
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
