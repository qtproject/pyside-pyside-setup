# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for QtAsyncio'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(True)

import shiboken6  # noqa: F401, E402
import asyncio  # noqa: E402


class QAsyncioLazyImportTestCase(unittest.TestCase):
    """PYSIDE-3471: Verify that the libshiboken's module import hook for lazy class
       loading does not interfere with the lazy import introduced in Python 3.15,
       which results in a lazy import being returned for concurrent.futures.ThreadPoolExecutor
       in the asyncio code."""
    def test(self):
        v = asyncio.run(asyncio.to_thread(lambda: 42))
        self.assertEqual(v, 42)


if __name__ == '__main__':
    unittest.main()
