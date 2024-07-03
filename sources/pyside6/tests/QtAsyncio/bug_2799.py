# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

"""Test cases for QtAsyncio"""

import unittest
import asyncio
import sys

import PySide6.QtAsyncio as QtAsyncio


@unittest.skipIf(sys.version_info < (3, 11), "Requires ExceptionGroup")
class QAsyncioTestCaseBug2799(unittest.TestCase):
    async def job(self):
        await asyncio.sleep(1)

    async def main(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.job())
            raise RuntimeError()

    def test_exception_group(self):
        with self.assertRaises(ExceptionGroup):
            QtAsyncio.run(self.main(), keep_running=False)


if __name__ == "__main__":
    unittest.main()
