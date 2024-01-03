# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtAsyncio'''

import unittest
import asyncio

from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QThread
from PySide6.QtAsyncio import QAsyncioEventLoopPolicy


class QAsyncioTestCaseExecutor(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.executor_thread = None

    def tearDown(self) -> None:
        super().tearDown()

    def blocking_function(self):
        self.executor_thread = QThread.currentThread()
        return 42

    async def run_asyncio_executor(self):
        main_thread = QThread.currentThread()
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = await asyncio.get_running_loop().run_in_executor(
                executor, self.blocking_function)

            # Assert that we are back to the main thread.
            self.assertEqual(QThread.currentThread(), main_thread)

            # Assert that the blocking function was executed in a different thread.
            self.assertNotEqual(self.executor_thread, main_thread)

            self.assertEqual(result, 42)

    def test_qasyncio_executor(self):
        asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
        asyncio.run(self.run_asyncio_executor())


if __name__ == '__main__':
    unittest.main()
