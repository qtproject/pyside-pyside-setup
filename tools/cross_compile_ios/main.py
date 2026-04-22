# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging

from ios_utilities import download_python_support


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    download_python_support()


if __name__ == "__main__":
    main()
