# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtAsyncio'''

import asyncio
import unittest

import PySide6.QtAsyncio as QtAsyncio


class QAsyncioTestCaseCancelTask(unittest.TestCase):
    # Taken from https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel

    async def cancel_me(self, output):
        output += "(1) cancel_me(): before sleep"

        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            output += "(2) cancel_me(): cancel sleep"
            raise
        finally:
            output += "(3) cancel_me(): after sleep"

    async def main(self, output):
        task = asyncio.create_task(self.cancel_me(output))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            output += "(4) main(): cancel_me is cancelled now"

    def test_await_tasks(self):
        output_expected = []
        output_real = []

        asyncio.run(self.main(output_expected))
        QtAsyncio.run(self.main(output_real), keep_running=False)

        self.assertEqual(output_real, output_expected)


if __name__ == '__main__':
    unittest.main()
