# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from . import events
from . import futures

import asyncio
import collections.abc
import concurrent.futures
import contextvars
import typing


class QAsyncioTask(futures.QAsyncioFuture):
    """ https://docs.python.org/3/library/asyncio-task.html """

    def __init__(self, coro: typing.Union[collections.abc.Generator, collections.abc.Coroutine], *,
                 loop: typing.Optional["events.QAsyncioEventLoop"] = None,
                 name: typing.Optional[str] = None,
                 context: typing.Optional[contextvars.Context] = None) -> None:
        super().__init__(loop=loop, context=context)

        self._coro = coro
        self._name = name if name else "QtTask"

        self._handle = self._loop.call_soon(self._step, context=self._context)

        self._cancellation_requests = 0

        asyncio._register_task(self)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        if self._state == futures.QAsyncioFuture.FutureState.PENDING:
            state = "Pending"
        elif self._state == futures.QAsyncioFuture.FutureState.DONE_WITH_RESULT:
            state = "Done"
        elif self._state == futures.QAsyncioFuture.FutureState.DONE_WITH_EXCEPTION:
            state = f"Done with exception ({repr(self._exception)})"
        elif self._state == futures.QAsyncioFuture.FutureState.CANCELLED:
            state = "Cancelled"

        return f"Task '{self.get_name()}' with state: {state}"

    class QtTaskApiMisuseError(Exception):
        pass

    def __await__(self) -> None:  # type: ignore[override]
        # This function is not inherited from the Future APIs.
        raise QAsyncioTask.QtTaskApiMisuseError("Tasks cannot be awaited")

    def __iter__(self) -> None:  # type: ignore[override]
        # This function is not inherited from the Future APIs.
        raise QAsyncioTask.QtTaskApiMisuseError("Tasks cannot be iterated over")

    def set_result(self, result: typing.Any) -> None:  # type: ignore[override]
        # This function is not inherited from the Future APIs.
        raise QAsyncioTask.QtTaskApiMisuseError("Tasks cannot set results")

    def set_exception(self, exception: typing.Any) -> None:  # type: ignore[override]
        # This function is not inherited from the Future APIs.
        raise QAsyncioTask.QtTaskApiMisuseError("Tasks cannot set exceptions")

    def _step(self,
              exception_or_future: typing.Union[
                  Exception, futures.QAsyncioFuture, None] = None) -> None:
        if self.done():
            return
        result = None

        try:
            asyncio._enter_task(self._loop, self)  # type: ignore[arg-type]
            if exception_or_future is None:
                result = self._coro.send(None)
            elif asyncio.futures.isfuture(exception_or_future):
                # If the future has an exception set by set_exception(), this will raise it.
                # If the future has been cancelled, this will raise CancelledError.
                # If the future's result isn't yet available, this will raise InvalidStateError.
                exception_or_future.result()
                exception_or_future = None
                result = self._coro.send(None)
            elif isinstance(exception_or_future, Exception):
                result = self._coro.throw(exception_or_future)
        except StopIteration as e:
            self._state = futures.QAsyncioFuture.FutureState.DONE_WITH_RESULT
            self._result = e.value
        except concurrent.futures.CancelledError as e:
            self._state = futures.QAsyncioFuture.FutureState.CANCELLED
            self._exception = e
        except Exception as e:
            self._state = futures.QAsyncioFuture.FutureState.DONE_WITH_EXCEPTION
            self._exception = e  # type: ignore[assignment]
        else:
            if asyncio.futures.isfuture(result):
                result.add_done_callback(
                    self._step, context=self._context)  # type: ignore[arg-type]
            else:
                self._loop.call_soon(self._step, exception_or_future, context=self._context)
        finally:
            asyncio._leave_task(self._loop, self)  # type: ignore[arg-type]
            if self._exception:
                self._loop.call_exception_handler({
                    "message": (str(self._exception) if self._exception
                                else "An exception occurred during task "
                                "execution"),
                    "exception": self._exception,
                    "task": self,
                    "future": (exception_or_future
                               if asyncio.futures.isfuture(exception_or_future)
                               else None)
                })
            if self.done():
                self._schedule_callbacks()
                asyncio._unregister_task(self)  # type: ignore[arg-type]

    def get_stack(self, *, limit=None) -> typing.List[typing.Any]:
        # TODO
        raise NotImplementedError("QtTask.get_stack is not implemented")

    def print_stack(self, *, limit=None, file=None) -> None:
        # TODO
        raise NotImplementedError("QtTask.print_stack is not implemented")

    def get_coro(self) -> typing.Union[collections.abc.Generator, collections.abc.Coroutine]:
        return self._coro

    def get_name(self) -> str:
        return self._name

    def set_name(self, value) -> None:
        self._name = str(value)

    def cancel(self, msg: typing.Optional[str] = None) -> bool:
        if self.done():
            return False
        if (isinstance(self._handle, events.QAsyncioHandle)):
            self._handle._cancel_exception_msg = msg
        self._cancel_message = msg
        self._handle.cancel()
        self._state = futures.QAsyncioFuture.FutureState.CANCELLED
        return True

    def uncancel(self) -> None:
        # TODO
        raise NotImplementedError("QtTask.uncancel is not implemented")

    def cancelling(self) -> bool:
        # TODO
        raise NotImplementedError("QtTask.cancelling is not implemented")
