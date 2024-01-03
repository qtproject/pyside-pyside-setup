# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtAsyncio'''

import unittest
import asyncio
import datetime

from PySide6.QtAsyncio import QAsyncioEventLoopPolicy


class QAsyncioTestCaseTime(unittest.TestCase):

    def setUp(self):
        self.previous_time = None
        self.exception = None

    def display_date(self, end_time, loop):
        if self.previous_time is not None:
            try:
                self.assertAlmostEqual(
                    (datetime.datetime.now() - self.previous_time).total_seconds(), 1, delta=0.1)
            except AssertionError as e:
                self.exception = e
        self.previous_time = datetime.datetime.now()
        if (loop.time() + 1.0) < end_time:
            loop.call_later(1, self.display_date, end_time, loop)
        else:
            loop.stop()

    def test_time(self):
        asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
        loop = asyncio.new_event_loop()

        end_time = loop.time() + 3.0
        loop.call_soon(self.display_date, end_time, loop)

        try:
            loop.run_forever()
        finally:
            loop.close()

        if self.exception is not None:
            raise self.exception


if __name__ == '__main__':
    unittest.main()
