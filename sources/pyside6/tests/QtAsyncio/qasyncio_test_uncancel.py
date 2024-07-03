# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

"""Test cases for QtAsyncio"""

import unittest
import asyncio

import PySide6.QtAsyncio as QtAsyncio


class QAsyncioTestCaseUncancel(unittest.TestCase):
    """ https://superfastpython.com/asyncio-cancel-task-cancellation """

    async def worker(self, outputs: list[str]):
        # Ensure the task always gets done.
        while True:
            try:
                await asyncio.sleep(2)
                outputs.append("Task sleep completed normally")
                break
            except asyncio.CancelledError:
                outputs.append("Task is cancelled, ignore and try again")
                asyncio.current_task().uncancel()

    async def main(self, outputs: list[str]):
        task = asyncio.create_task(self.worker(outputs))
        # Allow the task to run briefly.
        await asyncio.sleep(0.5)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            outputs.append("Task was cancelled")

        cancelling = task.cancelling()
        self.assertEqual(cancelling, 0)
        outputs.append(f"Task cancelling: {cancelling}")

        cancelled = task.cancelled()
        self.assertFalse(cancelled)
        outputs.append(f"Task cancelled: {cancelled}")

        done = task.done()
        self.assertTrue(done)
        outputs.append(f"Task done: {done}")

    def test_uncancel(self):
        outputs_expected = []
        outputs_real = []

        asyncio.run(self.main(outputs_real))
        QtAsyncio.run(self.main(outputs_expected), keep_running=False)

        self.assertIsNotNone(outputs_real)
        self.assertEqual(outputs_real, outputs_expected)


if __name__ == "__main__":
    unittest.main()
