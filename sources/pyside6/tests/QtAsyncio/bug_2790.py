# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for QtAsyncio'''

import unittest
import asyncio

import PySide6.QtAsyncio as QtAsyncio


class QAsyncioTestCaseBug2790(unittest.TestCase):

    async def producer(self, products: list[str]):
        while True:
            products.append("product")
            await asyncio.sleep(2)

    async def task(self, outputs: list[str]):
        products = []
        asyncio.ensure_future(self.producer(products))
        for _ in range(6):
            try:
                async with asyncio.timeout(0.5):
                    while len(products) == 0:
                        await asyncio.sleep(0)
                    outputs.append(products.pop(0))
            except TimeoutError:
                outputs.append("Timeout")

    def test_timeout(self):
        # The Qt event loop (and thus QtAsyncio) does not guarantee that events
        # will be processed in the order they were posted, so there is two
        # possible outputs for this test.
        outputs_expected_1 = ["product", "Timeout", "Timeout", "Timeout", "Timeout", "product"]
        outputs_expected_2 = ["product", "Timeout", "Timeout", "Timeout", "product", "Timeout"]

        outputs_real = []

        QtAsyncio.run(self.task(outputs_real), keep_running=False)

        self.assertTrue(outputs_real in [outputs_expected_1, outputs_expected_2])


if __name__ == '__main__':
    unittest.main()
