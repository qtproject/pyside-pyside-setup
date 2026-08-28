# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:significant reason:build-tool
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PyProjectParseResult:
    errors: list[str] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)
    rcc_options: list[str] = field(default_factory=list)
    uic_options: list[str] = field(default_factory=list)
