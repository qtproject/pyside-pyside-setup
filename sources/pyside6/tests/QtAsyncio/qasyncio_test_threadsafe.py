# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtAsyncio'''

import unittest
import asyncio
import threading
import time

from PySide6.QtAsyncio import QAsyncioEventLoopPolicy


class QAsyncioTestCaseThreadsafe(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
        self.loop_event = asyncio.Event()

    def thread_target(self, is_threadsafe):
        time.sleep(1)
        if is_threadsafe:
            # call_soon_threadsafe() wakes the loop that is in another thread, so the
            # loop checks the event and will not hang.
            asyncio.get_event_loop().call_soon_threadsafe(self.loop_event.set)
        else:
            # call_soon() does not wake the loop that is in another thread, and so the
            # loop keeps waiting without checking the event and will hang.
            asyncio.get_event_loop().call_soon(self.loop_event.set)

    async def coro(self, is_threadsafe):
        thread = threading.Thread(target=self.thread_target, args=(is_threadsafe,))
        thread.start()

        task = asyncio.create_task(self.loop_event.wait())

        # The timeout is necessary because the loop will hang for the non-threadsafe case.
        done, pending = await asyncio.wait([task], timeout=2)

        thread.join()

        if is_threadsafe:
            self.assertEqual(len(done), 1)
            self.assertEqual(len(pending), 0)
        else:
            self.assertEqual(len(done), 0)
            self.assertEqual(len(pending), 1)

    def test_not_threadsafe(self):
        asyncio.run(self.coro(False))

    def test_threadsafe(self):
        asyncio.run(self.coro(True))


if __name__ == '__main__':
    unittest.main()
