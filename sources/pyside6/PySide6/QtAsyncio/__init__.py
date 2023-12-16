# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from .events import (
    QAsyncioEventLoopPolicy, QAsyncioEventLoop, QAsyncioHandle, QAsyncioTimerHandle
)
from .futures import QAsyncioFuture
from .tasks import QAsyncioTask

import asyncio
import typing

__all__ = [
    "QAsyncioEventLoopPolicy", "QAsyncioEventLoop",
    "QAsyncioHandle", "QAsyncioTimerHandle",
    "QAsyncioFuture", "QAsyncioTask"
]


def run(coro: typing.Optional[typing.Coroutine] = None, *,
        debug: typing.Optional[bool] = None) -> None:
    """Run the event loop."""
    asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
    if coro:
        asyncio.ensure_future(coro)
    asyncio.run(asyncio.Event().wait(), debug=debug)
