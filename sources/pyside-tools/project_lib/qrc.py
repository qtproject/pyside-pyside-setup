# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def qrc_file_requires_rebuild(resources_file_path: Path, compiled_resources_path: Path) -> bool:
    """Returns whether a compiled qrc file needs to be rebuilt based on the files that references"""
    root_element = ET.parse(resources_file_path).getroot()
    project_root = resources_file_path.parent

    files = [project_root / file.text for file in root_element.findall(".//file")]

    compiled_resources_time = compiled_resources_path.stat().st_mtime
    # If any of the resource files has been modified after the compiled qrc file, the compiled qrc
    # file needs to be rebuilt
    if any(file.is_file() and file.stat().st_mtime > compiled_resources_time for file in files):
        return True
    return False
