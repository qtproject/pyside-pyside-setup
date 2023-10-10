# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from PySide6.QtCore import QDateTime, QCoreApplication, QTimer, QThread, Slot

from . import futures
from . import tasks

import asyncio
import collections.abc
import concurrent.futures
import contextvars
import enum
import os
import socket
import subprocess
import typing

__all__ = [
    "QAsyncioEventLoopPolicy", "QAsyncioEventLoop",
    "QAsyncioHandle", "QAsyncioTimerHandle",
]


class QAsyncioEventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    def __init__(self, application: typing.Optional[QCoreApplication] = None) -> None:
        super().__init__()
        if application is None:
            if QCoreApplication.instance() is None:
                application = QCoreApplication()
            else:
                application = QCoreApplication.instance()
        self._application: QCoreApplication = application  # type: ignore[assignment]
        self._event_loop: typing.Optional[asyncio.AbstractEventLoop] = None

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        if self._event_loop is None:
            self._event_loop = QAsyncioEventLoop(self._application)
        return self._event_loop

    def set_event_loop(self, loop: typing.Optional[asyncio.AbstractEventLoop]) -> None:
        self._event_loop = loop

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        return QAsyncioEventLoop(self._application)


class QAsyncioEventLoop(asyncio.BaseEventLoop):
    """
    Implements the asyncio API:
    https://docs.python.org/3/library/asyncio-eventloop.html
    """

    class ShutDownThread(QThread):
        def __init__(self, future: futures.QAsyncioFuture, loop: "QAsyncioEventLoop") -> None:
            super().__init__()
            self._future = future
            self._loop = loop
            self.started.connect(self.shutdown)

        def run(self) -> None:
            pass

        def shutdown(self) -> None:
            try:
                self._loop._default_executor.shutdown(wait=True)
                if not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(self._future.set_result, None)
            except Exception as e:
                if not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(self._future.set_exception, e)

    def __init__(self, application: QCoreApplication) -> None:
        super().__init__()

        self._application: QCoreApplication = application
        self._thread = QThread.currentThread()

        self._closed = False

        self._quit_from_inside = False
        self._quit_from_outside = False

        self._asyncgens: typing.Set[collections.abc.AsyncGenerator] = set()

        # Starting with Python 3.11, this must be an instance of
        # ThreadPoolExecutor.
        self._default_executor = concurrent.futures.ThreadPoolExecutor()

        self._exception_handler: typing.Optional[typing.Callable] = self.default_exception_handler
        self._task_factory: typing.Optional[typing.Callable] = None
        self._future_to_complete: typing.Optional[futures.QAsyncioFuture] = None

        self._debug = bool(os.getenv("PYTHONASYNCIODEBUG", False))

        self._application.aboutToQuit.connect(self._about_to_quit_cb)

    # Running and stopping the loop

    def _run_until_complete_cb(self, future: futures.QAsyncioFuture) -> None:
        if not future.cancelled():
            if isinstance(future.exception(), (SystemExit, KeyboardInterrupt)):
                return
        future.get_loop().stop()

    def run_until_complete(self, future: futures.QAsyncioFuture) -> typing.Any:  # type: ignore[override]
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        if self.is_running():
            raise RuntimeError("Event loop is already running")

        arg_was_coro = not asyncio.futures.isfuture(future)
        future = asyncio.tasks.ensure_future(future, loop=self)  # type: ignore[assignment]
        future.add_done_callback(self._run_until_complete_cb)
        self._future_to_complete = future

        try:
            self.run_forever()
        except Exception as e:
            if arg_was_coro and future.done() and not future.cancelled():
                future.exception()
            raise e
        finally:
            future.remove_done_callback(self._run_until_complete_cb)
        if not future.done():
            raise RuntimeError("Event loop stopped before Future completed")

        return future.result()

    def run_forever(self) -> None:
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        if self.is_running():
            raise RuntimeError("Event loop is already running")
        asyncio.events._set_running_loop(self)
        self._application.exec()
        asyncio.events._set_running_loop(None)

    def _about_to_quit_cb(self):
        if not self._quit_from_inside:
            self._quit_from_outside = True

    def stop(self) -> None:
        if self._future_to_complete is not None:
            if self._future_to_complete.done():
                self._future_to_complete = None
            else:
                return
        self._quit_from_inside = True
        self._application.quit()

    def is_running(self) -> bool:
        return self._thread.loopLevel() > 0

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self.is_running():
            raise RuntimeError("Cannot close a running event loop")
        if self.is_closed():
            return
        if self._default_executor is not None:
            self._default_executor.shutdown(wait=False)
        self._application.shutdown()
        self._closed = True

    async def shutdown_asyncgens(self) -> None:
        if not len(self._asyncgens):
            return

        results = await asyncio.tasks.gather(
            *[asyncgen.aclose() for asyncgen in self._asyncgens],
            return_exceptions=True)

        for result, asyncgen in zip(results, self._asyncgens):
            if isinstance(result, Exception):
                self.call_exception_handler({
                    "message": f"Closing asynchronous generator {asyncgen}"
                               f"raised an exception",
                    "exception": result,
                    "asyncgen": asyncgen})

        self._asyncgens.clear()

    async def shutdown_default_executor(self) -> None:
        if self._default_executor is None:
            return
        future = self.create_future()
        thread = QAsyncioEventLoop.ShutDownThread(future, self)
        thread.start()
        try:
            await future
        finally:
            thread.wait()

    # Scheduling callbacks

    def call_soon(self, callback: typing.Callable, *args: typing.Any,
                  context: typing.Optional[contextvars.Context] = None):
        return self.call_later(0, callback, *args, context=context)

    def call_soon_threadsafe(self, callback: typing.Callable,  # type: ignore[override]
                             *args: typing.Any,
                             context:
                             typing.Optional[contextvars.Context] = None) -> "QAsyncioHandle":
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        return self.call_soon(callback, *args, context=context)

    def call_later(self, delay: typing.Union[int, float],  # type: ignore[override]
                   callback: typing.Callable, *args: typing.Any,
                   context: typing.Optional[contextvars.Context] = None) -> "QAsyncioHandle":
        if not isinstance(delay, (int, float)):
            raise TypeError("delay must be an int or float")
        return self.call_at(self.time() + delay, callback, *args,
                            context=context)

    def call_at(self, when: typing.Union[int, float],  # type: ignore[override]
                callback: typing.Callable, *args: typing.Any,
                context: typing.Optional[contextvars.Context] = None) -> "QAsyncioHandle":
        if not isinstance(when, (int, float)):
            raise TypeError("when must be an int or float")
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        return QAsyncioTimerHandle(when, callback, args, self, context)

    def time(self) -> float:
        return QDateTime.currentMSecsSinceEpoch() / 1000

    # Creating Futures and Tasks

    def create_future(self) -> futures.QAsyncioFuture:  # type: ignore[override]
        return futures.QAsyncioFuture(loop=self)

    def create_task(self,  # type: ignore[override]
                    coro: typing.Union[collections.abc.Generator, collections.abc.Coroutine],
                    *, name: typing.Optional[str] = None,
                    context: typing.Optional[contextvars.Context] = None) -> tasks.QAsyncioTask:
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        if self._task_factory is None:
            task = tasks.QAsyncioTask(coro, loop=self, name=name, context=context)
        else:
            task = self._task_factory(self, coro, context=context)
            task.set_name(name)

        return task

    def set_task_factory(self, factory: typing.Optional[typing.Callable]) -> None:
        if factory is not None and not callable(factory):
            raise TypeError("The task factory must be a callable or None")
        self._task_factory = factory

    def get_task_factory(self) -> typing.Optional[typing.Callable]:
        return self._task_factory

    # Opening network connections

    async def create_connection(
            self, protocol_factory, host=None, port=None,
            *, ssl=None, family=0, proto=0,
            flags=0, sock=None, local_addr=None,
            server_hostname=None,
            ssl_handshake_timeout=None,
            ssl_shutdown_timeout=None,
            happy_eyeballs_delay=None, interleave=None):
        raise NotImplementedError

    async def create_datagram_endpoint(self, protocol_factory,
                                       local_addr=None, remote_addr=None, *,
                                       family=0, proto=0, flags=0,
                                       reuse_address=None, reuse_port=None,
                                       allow_broadcast=None, sock=None):
        raise NotImplementedError

    async def create_unix_connection(
            self, protocol_factory, path=None, *,
            ssl=None, sock=None,
            server_hostname=None,
            ssl_handshake_timeout=None,
            ssl_shutdown_timeout=None):
        raise NotImplementedError

    # Creating network servers

    async def create_server(
            self, protocol_factory, host=None, port=None,
            *, family=socket.AF_UNSPEC,
            flags=socket.AI_PASSIVE, sock=None, backlog=100,
            ssl=None, reuse_address=None, reuse_port=None,
            ssl_handshake_timeout=None,
            ssl_shutdown_timeout=None,
            start_serving=True):
        raise NotImplementedError

    async def create_unix_server(
            self, protocol_factory, path=None, *,
            sock=None, backlog=100, ssl=None,
            ssl_handshake_timeout=None,
            ssl_shutdown_timeout=None,
            start_serving=True):
        raise NotImplementedError

    async def connect_accepted_socket(
            self, protocol_factory, sock,
            *, ssl=None,
            ssl_handshake_timeout=None,
            ssl_shutdown_timeout=None):
        raise NotImplementedError

    # Transferring files

    async def sendfile(self, transport, file, offset=0, count=None,
                       *, fallback=True):
        raise NotImplementedError

    # TLS Upgrade

    async def start_tls(self, transport, protocol, sslcontext, *,
                        server_side=False,
                        server_hostname=None,
                        ssl_handshake_timeout=None,
                        ssl_shutdown_timeout=None):
        raise NotImplementedError

    # Watching file descriptors

    def add_reader(self, fd, callback, *args):
        raise NotImplementedError

    def remove_reader(self, fd):
        raise NotImplementedError

    def add_writer(self, fd, callback, *args):
        raise NotImplementedError

    def remove_writer(self, fd):
        raise NotImplementedError

    # Working with socket objects directly

    async def sock_recv(self, sock, nbytes):
        raise NotImplementedError

    async def sock_recv_into(self, sock, buf):
        raise NotImplementedError

    async def sock_recvfrom(self, sock, bufsize):
        raise NotImplementedError

    async def sock_recvfrom_into(self, sock, buf, nbytes=0):
        raise NotImplementedError

    async def sock_sendall(self, sock, data):
        raise NotImplementedError

    async def sock_sendto(self, sock, data, address):
        raise NotImplementedError

    async def sock_connect(self, sock, address):
        raise NotImplementedError

    async def sock_accept(self, sock):
        raise NotImplementedError

    async def sock_sendfile(self, sock, file, offset=0, count=None, *,
                            fallback=None):
        raise NotImplementedError

    # DNS

    async def getaddrinfo(self, host, port, *,
                          family=0, type=0, proto=0, flags=0):
        raise NotImplementedError

    async def getnameinfo(self, sockaddr, flags=0):
        raise NotImplementedError

    # Working with pipes

    async def connect_read_pipe(self, protocol_factory, pipe):
        raise NotImplementedError

    async def connect_write_pipe(self, protocol_factory, pipe):
        raise NotImplementedError

    # Unix signals

    def add_signal_handler(self, sig, callback, *args):
        raise NotImplementedError

    def remove_signal_handler(self, sig):
        raise NotImplementedError

    # Executing code in thread or process pools

    def run_in_executor(self,
                        executor: typing.Optional[concurrent.futures.ThreadPoolExecutor],
                        func: typing.Callable, *args: typing.Tuple) -> asyncio.futures.Future:
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        if executor is None:
            executor = self._default_executor
        return asyncio.futures.wrap_future(
            executor.submit(func, *args), loop=self
        )

    def set_default_executor(self,
                             executor: typing.Optional[
                                 concurrent.futures.ThreadPoolExecutor]) -> None:
        if not isinstance(executor, concurrent.futures.ThreadPoolExecutor):
            raise TypeError("The executor must be a ThreadPoolExecutor")
        self._default_executor = executor

    # Error Handling API

    def set_exception_handler(self, handler: typing.Optional[typing.Callable]) -> None:
        if handler is not None and not callable(handler):
            raise TypeError("The handler must be a callable or None")
        self._exception_handler = handler

    def get_exception_handler(self) -> typing.Optional[typing.Callable]:
        return self._exception_handler

    def default_exception_handler(self, context: typing.Dict[str, typing.Any]) -> None:
        # TODO
        print(context["message"])

    def call_exception_handler(self, context: typing.Dict[str, typing.Any]) -> None:
        if self._exception_handler is not None:
            self._exception_handler(context)

    # Enabling debug mode

    def get_debug(self) -> bool:
        # TODO: Part of the asyncio API but currently unused. More details:
        # https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode
        return self._debug

    def set_debug(self, enabled: bool) -> None:
        self._debug = enabled

    # Running subprocesses

    async def subprocess_exec(self, protocol_factory, *args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              **kwargs):
        raise NotImplementedError

    async def subprocess_shell(self, protocol_factory, cmd, *,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               **kwargs):
        raise NotImplementedError


class QAsyncioHandle():
    class HandleState(enum.Enum):
        PENDING = enum.auto()
        CANCELLED = enum.auto()
        DONE = enum.auto()

    def __init__(self, callback: typing.Callable, args: typing.Tuple,
                 loop: QAsyncioEventLoop, context: typing.Optional[contextvars.Context]) -> None:
        self._cancel_exception_msg: typing.Optional[str] = None

        self._callback = callback
        self._args = args
        self._loop = loop
        self._context = context

        self._timeout = 0

        self._state = QAsyncioHandle.HandleState.PENDING
        self._start()

    def _schedule_event(self, timeout: int, func: typing.Callable) -> None:
        if not self._loop.is_closed() and not self._loop._quit_from_outside:
            QTimer.singleShot(timeout, func)

    def _start(self) -> None:
        self._schedule_event(self._timeout, lambda: self._cb())

    @Slot()
    def _cb(self) -> None:
        if self._state == QAsyncioHandle.HandleState.PENDING:
            if self._context is not None:
                self._context.run(self._callback, *self._args)
            else:
                self._callback(*self._args)
            self._state = QAsyncioHandle.HandleState.DONE

    @Slot()
    def _cancel_exception(self) -> None:
        raise asyncio.CancelledError(self._cancel_exception_msg)

    def cancel(self) -> None:
        if self._state == QAsyncioHandle.HandleState.PENDING:
            self._state = QAsyncioHandle.HandleState.CANCELLED
            # The old timer that was created in _start will still trigger but _cb won't do anything.
            self._schedule_event(0, lambda: self._cancel_exception())

    def cancelled(self) -> bool:
        return self._state == QAsyncioHandle.HandleState.CANCELLED


class QAsyncioTimerHandle(QAsyncioHandle):
    def __init__(self, when: float, callback: typing.Callable, args: typing.Tuple,
                 loop: QAsyncioEventLoop, context: typing.Optional[contextvars.Context]) -> None:
        super().__init__(callback, args, loop, context)

        self._when = when
        self._timeout = int(max(self._when - self._loop.time(), 0) * 1000)

        super()._start()

    # Override this so that timer.start() is only called once at the end
    # of the constructor for both QtHandle and QtTimerHandle.
    def _start(self) -> None:
        pass

    def when(self) -> float:
        return self._when
