# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from PySide6.QtCore import (QCoreApplication, QDateTime, QDeadlineTimer,
                            QEventLoop, QObject, QTimer, QThread, Slot)

from . import futures
from . import tasks

import asyncio
import collections.abc
import concurrent.futures
import contextvars
import enum
import os
import signal
import socket
import subprocess
import typing
import warnings

__all__ = [
    "QAsyncioEventLoopPolicy", "QAsyncioEventLoop",
    "QAsyncioHandle", "QAsyncioTimerHandle",
]


class QAsyncioExecutorWrapper(QObject):
    """
    Executors in asyncio allow running synchronous code in a separate thread or
    process without blocking the event loop or interrupting the asynchronous
    program flow. Callables are scheduled for execution by calling submit() or
    map() on an executor object.

    Executors require a bit of extra work for QtAsyncio, as we can't use
    naked Python threads; instead, we must make sure that the thread created
    by executor.submit() has an event loop. This is achieved by not submitting
    the callable directly, but a small wrapper that attaches a QEventLoop to
    the executor thread, and then creates a zero-delay singleshot timer to push
    the actual callable for the executor into this new event loop.
    """

    def __init__(self, func: typing.Callable, *args: typing.Tuple) -> None:
        super().__init__()
        self._loop: QEventLoop
        self._func = func
        self._args = args
        self._result = None
        self._exception = None

    def _cb(self):
        try:
            # Call the synchronous callable that we submitted with submit() or
            # map().
            self._result = self._func(*self._args)
        except BaseException as e:
            self._exception = e
        self._loop.exit()

    def do(self):
        # This creates a new event loop and dispatcher for the thread, if not
        # already created.
        self._loop = QEventLoop()
        asyncio.events._set_running_loop(self._loop)

        QTimer.singleShot(0, self._loop, lambda: self._cb())

        self._loop.exec()
        if self._exception is not None:
            raise self._exception
        return self._result

    def exit(self):
        self._loop.exit()


class QAsyncioEventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    """
    Event loop policies are expected to be deprecated with Python 3.13, with
    subsequent removal in Python 3.15. At that point, part of the current
    logic of the QAsyncioEventLoopPolicy constructor will have to be moved
    to QtAsyncio.run() and/or to a loop factory class (to be provided as an
    argument to asyncio.run()). In particular, this concerns the logic of
    setting up the QCoreApplication and the SIGINT handler.

    More details:
    https://discuss.python.org/t/removing-the-asyncio-policy-system-asyncio-set-event-loop-policy-in-python-3-15/37553
    """
    def __init__(self,
                 application: typing.Optional[QCoreApplication] = None,
                 quit_qapp: bool = True,
                 handle_sigint: bool = False) -> None:
        super().__init__()
        if application is None:
            if QCoreApplication.instance() is None:
                application = QCoreApplication()
            else:
                application = QCoreApplication.instance()
        self._application: QCoreApplication = application  # type: ignore[assignment]

        # Configure whether the QCoreApplication at the core of QtAsyncio
        # should be shut down when asyncio finishes. A special case where one
        # would want to disable this is test suites that want to reuse a single
        # QCoreApplication instance across all unit tests, which would fail if
        # this instance is shut down every time.
        self._quit_qapp = quit_qapp

        self._event_loop: typing.Optional[asyncio.AbstractEventLoop] = None

        if handle_sigint:
            signal.signal(signal.SIGINT, signal.SIG_DFL)

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        if self._event_loop is None:
            self._event_loop = QAsyncioEventLoop(self._application, quit_qapp=self._quit_qapp)
        return self._event_loop

    def set_event_loop(self, loop: typing.Optional[asyncio.AbstractEventLoop]) -> None:
        self._event_loop = loop

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        return QAsyncioEventLoop(self._application, quit_qapp=self._quit_qapp)

    def get_child_watcher(self) -> "asyncio.AbstractChildWatcher":
        raise DeprecationWarning("Child watchers are deprecated since Python 3.12")

    def set_child_watcher(self, watcher: "asyncio.AbstractChildWatcher") -> None:
        raise DeprecationWarning("Child watchers are deprecated since Python 3.12")


class QAsyncioEventLoop(asyncio.BaseEventLoop, QObject):
    """
    Implements the asyncio API:
    https://docs.python.org/3/library/asyncio-eventloop.html
    """

    class ShutDownThread(QThread):
        """
        Used to shut down the default executor when calling
        shutdown_default_executor(). As the executor is a ThreadPoolExecutor,
        it must be shut down in a separate thread as all the threads from the
        thread pool must join, which we want to do without blocking the event
        loop.
        """

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

    def __init__(self,
                 application: QCoreApplication, quit_qapp: bool = True) -> None:
        asyncio.BaseEventLoop.__init__(self)
        QObject.__init__(self)

        self._application: QCoreApplication = application

        # Configure whether the QCoreApplication at the core of QtAsyncio
        # should be shut down when asyncio finishes. A special case where one
        # would want to disable this is test suites that want to reuse a single
        # QCoreApplication instance across all unit tests, which would fail if
        # this instance is shut down every time.
        self._quit_qapp = quit_qapp

        self._thread = QThread.currentThread()

        self._closed = False

        # These two flags are used to determine whether the loop was stopped
        # from inside the loop (i.e., coroutine or callback called stop()) or
        # from outside the loop (i.e., the QApplication is being shut down, for
        # example, by the user closing the window or by calling
        # QApplication.quit()). The different cases can trigger slightly
        # different behaviors (see the comments where the flags are used).
        # There are two variables for this as in a third case the loop is still
        # running and both flags are False.
        self._quit_from_inside = False
        self._quit_from_outside = False

        # A set of all asynchronous generators that are currently running.
        self._asyncgens: typing.Set[collections.abc.AsyncGenerator] = set()

        # Starting with Python 3.11, this must be an instance of
        # ThreadPoolExecutor.
        self._default_executor = concurrent.futures.ThreadPoolExecutor()

        # The exception handler, if set with set_exception_handler(). The
        # exception handler is currently called in two places: One, if an
        # asynchonrous generator raises an exception when closed, and two, if
        # an exception is raised during the execution of a task. Currently, the
        # default exception handler just prints the exception to the console.
        self._exception_handler: typing.Optional[typing.Callable] = self.default_exception_handler

        # The task factory, if set with set_task_factory(). Otherwise, a new
        # task is created with the QAsyncioTask constructor.
        self._task_factory: typing.Optional[typing.Callable] = None

        # The future that is currently being awaited with run_until_complete().
        self._future_to_complete: typing.Optional[futures.QAsyncioFuture] = None

        self._debug = bool(os.getenv("PYTHONASYNCIODEBUG", False))

        self._application.aboutToQuit.connect(self._about_to_quit_cb)

    # Running and stopping the loop

    def _run_until_complete_cb(self, future: futures.QAsyncioFuture) -> None:
        """
        A callback that stops the loop when the future is done, used when
        running the loop with run_until_complete().
        """
        if not future.cancelled():
            if isinstance(future.exception(), (SystemExit, KeyboardInterrupt)):
                return
        future.get_loop().stop()

    def run_until_complete(self,
                           future: futures.QAsyncioFuture) -> typing.Any:  # type: ignore[override]
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
        """ A callback for the aboutToQuit signal of the QCoreApplication. """
        if not self._quit_from_inside:
            # If the aboutToQuit signal is emitted, the user is closing the
            # application window or calling QApplication.quit(). In this case,
            # we want to close the event loop, and we consider this a quit from
            # outside the loop.
            self._quit_from_outside = True
            self.close()

    def stop(self) -> None:
        if self._future_to_complete is not None:
            if self._future_to_complete.done():
                self._future_to_complete = None
            else:
                # Do not stop the loop if there is a future still being awaited
                # with run_until_complete().
                return

        self._quit_from_inside = True

        # The user might want to keep the QApplication running after the event
        # event loop finishes, which they can control with the quit_qapp
        # argument.
        if self._quit_qapp:
            self._application.quit()

    def is_running(self) -> bool:
        return self._thread.loopLevel() > 0

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self.is_running() and not self._quit_from_outside:
            raise RuntimeError("Cannot close a running event loop")
        if self.is_closed():
            return
        if self._default_executor is not None:
            self._default_executor.shutdown(wait=False)
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

    async def shutdown_default_executor(self,  # type: ignore[override]
                                        timeout: typing.Union[int, float, None] = None) -> None:
        shutdown_successful = False
        if timeout is not None:
            deadline_timer = QDeadlineTimer(int(timeout * 1000))
        else:
            deadline_timer = QDeadlineTimer(QDeadlineTimer.Forever)

        if self._default_executor is None:
            return
        future = self.create_future()
        thread = QAsyncioEventLoop.ShutDownThread(future, self)
        thread.start()
        try:
            await future
        finally:
            shutdown_successful = thread.wait(deadline_timer)

        if timeout is not None and not shutdown_successful:
            warnings.warn(
                f"Could not shutdown the default executor within {timeout} seconds",
                RuntimeWarning, stacklevel=2)
            self._default_executor.shutdown(wait=False)

    # Scheduling callbacks

    def _call_soon_impl(self, callback: typing.Callable, *args: typing.Any,
                        context: typing.Optional[contextvars.Context] = None,
                        is_threadsafe: typing.Optional[bool] = False) -> asyncio.Handle:
        return self._call_later_impl(0, callback, *args, context=context,
                                     is_threadsafe=is_threadsafe)

    def call_soon(self, callback: typing.Callable, *args: typing.Any,
                  context: typing.Optional[contextvars.Context] = None) -> asyncio.Handle:
        return self._call_soon_impl(callback, *args, context=context, is_threadsafe=False)

    def call_soon_threadsafe(self, callback: typing.Callable, *args: typing.Any,
                             context:
                             typing.Optional[contextvars.Context] = None) -> asyncio.Handle:
        if self.is_closed():
            raise RuntimeError("Event loop is closed")
        if context is None:
            context = contextvars.copy_context()
        return self._call_soon_impl(callback, *args, context=context, is_threadsafe=True)

    def _call_later_impl(self, delay: typing.Union[int, float],
                         callback: typing.Callable, *args: typing.Any,
                         context: typing.Optional[contextvars.Context] = None,
                         is_threadsafe: typing.Optional[bool] = False) -> asyncio.TimerHandle:
        if not isinstance(delay, (int, float)):
            raise TypeError("delay must be an int or float")
        return self._call_at_impl(self.time() + delay, callback, *args, context=context,
                                  is_threadsafe=is_threadsafe)

    def call_later(self, delay: typing.Union[int, float],
                   callback: typing.Callable, *args: typing.Any,
                   context: typing.Optional[contextvars.Context] = None) -> asyncio.TimerHandle:
        return self._call_later_impl(delay, callback, *args, context=context, is_threadsafe=False)

    def _call_at_impl(self, when: typing.Union[int, float],
                      callback: typing.Callable, *args: typing.Any,
                      context: typing.Optional[contextvars.Context] = None,
                      is_threadsafe: typing.Optional[bool] = False) -> asyncio.TimerHandle:
        """ All call_at() and call_later() methods map to this method. """
        if not isinstance(when, (int, float)):
            raise TypeError("when must be an int or float")
        return QAsyncioTimerHandle(when, callback, args, self, context, is_threadsafe=is_threadsafe)

    def call_at(self, when: typing.Union[int, float],
                callback: typing.Callable, *args: typing.Any,
                context: typing.Optional[contextvars.Context] = None) -> asyncio.TimerHandle:
        return self._call_at_impl(when, callback, *args, context=context, is_threadsafe=False)

    def time(self) -> float:
        return QDateTime.currentMSecsSinceEpoch() / 1000

    # Creating Futures and Tasks

    def create_future(self) -> futures.QAsyncioFuture:  # type: ignore[override]
        return futures.QAsyncioFuture(loop=self)

    def create_task(self,  # type: ignore[override]
                    coro: typing.Union[collections.abc.Generator, collections.abc.Coroutine],
                    *, name: typing.Optional[str] = None,
                    context: typing.Optional[contextvars.Context] = None) -> tasks.QAsyncioTask:
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

        # Executors require a bit of extra work for QtAsyncio, as we can't use
        # naked Python threads; instead, we must make sure that the thread
        # created by executor.submit() has an event loop. This is achieved by
        # not submitting the callable directly, but a small wrapper that
        # attaches a QEventLoop to the executor thread, and then pushes the
        # actual callable for the executor into this new event loop.
        wrapper = QAsyncioExecutorWrapper(func, *args)
        return asyncio.futures.wrap_future(
            executor.submit(wrapper.do), loop=self
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
        if context["message"]:
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
    """
    The handle enqueues a callback to be executed by the event loop, and allows
    for this callback to be cancelled before it is executed. This callback will
    typically execute the step function for a task. This makes the handle one
    of the main components of asyncio.
    """
    class HandleState(enum.Enum):
        PENDING = enum.auto()
        CANCELLED = enum.auto()
        DONE = enum.auto()

    def __init__(self, callback: typing.Callable, args: typing.Tuple,
                 loop: QAsyncioEventLoop, context: typing.Optional[contextvars.Context],
                 is_threadsafe: typing.Optional[bool] = False) -> None:
        self._callback = callback
        self._args = args
        self._loop = loop
        self._context = context
        self._is_threadsafe = is_threadsafe

        self._timeout = 0

        self._state = QAsyncioHandle.HandleState.PENDING
        self._start()

    def _start(self) -> None:
        self._schedule_event(self._timeout, lambda: self._cb())

    def _schedule_event(self, timeout: int, func: typing.Callable) -> None:
        # Do not schedule events from asyncio when the app is quit from outside
        # the event loop, as this would cause events to be enqueued after the
        # event loop was destroyed.
        if not self._loop.is_closed() and not self._loop._quit_from_outside:
            if self._is_threadsafe:
                # This singleShot overload will push func into self._loop
                # instead of the current thread's loop. This allows scheduling
                # a callback from a different thread, which is necessary for
                # thread-safety.
                # https://docs.python.org/3/library/asyncio-dev.html#asyncio-multithreading
                QTimer.singleShot(timeout, self._loop, func)
            else:
                QTimer.singleShot(timeout, func)

    @Slot()
    def _cb(self) -> None:
        """
        A slot, enqueued into the event loop, that wraps around the actual
        callback, typically the step function of a task.
        """
        if self._state == QAsyncioHandle.HandleState.PENDING:
            if self._context is not None:
                self._context.run(self._callback, *self._args)
            else:
                self._callback(*self._args)
            self._state = QAsyncioHandle.HandleState.DONE

    def cancel(self) -> None:
        if self._state == QAsyncioHandle.HandleState.PENDING:
            # The old timer that was created in _start will still trigger but
            # _cb won't do anything, therefore the callback is effectively
            # cancelled.
            self._state = QAsyncioHandle.HandleState.CANCELLED

    def cancelled(self) -> bool:
        return self._state == QAsyncioHandle.HandleState.CANCELLED


class QAsyncioTimerHandle(QAsyncioHandle, asyncio.TimerHandle):
    def __init__(self, when: float, callback: typing.Callable, args: typing.Tuple,
                 loop: QAsyncioEventLoop, context: typing.Optional[contextvars.Context],
                 is_threadsafe: typing.Optional[bool] = False) -> None:
        QAsyncioHandle.__init__(self, callback, args, loop, context, is_threadsafe)

        self._when = when
        time = self._loop.time()
        self._timeout = round(max(self._when - time, 0) * 1000)

        QAsyncioHandle._start(self)

    def _start(self) -> None:
        """
        Overridden so that timer.start() is only called once at the end of the
        constructor for both QtHandle and QtTimerHandle.
        """
        pass

    def when(self) -> float:
        return self._when
