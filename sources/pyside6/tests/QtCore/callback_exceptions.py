# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import unittest
import sys
import os
from types import TracebackType

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

import shiboken6  # noqa: E402
from PySide6.QtCore import (  # noqa: E402
    QTimer,
    qInstallMessageHandler,
    QtMsgType,
    QMessageLogContext,
    qInfo,
    QThreadPool,
    QRunnable,
    QCameraPermission,
    QObject,
)
from PySide6.QtCore import QCoreApplication  # noqa: E402


class MyException(Exception):
    pass


class TestQtException(unittest.TestCase):
    unhandled: list[BaseException] = []
    old_excepthook = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.old_excepthook = sys.excepthook

        def excepthook(
            type: type[BaseException],
            value: BaseException,
            traceback: TracebackType | None,
        ) -> None:
            cls.unhandled.append(value)
            if not isinstance(value, MyException):
                cls.old_excepthook(type, value, traceback)

        sys.excepthook = excepthook

    @classmethod
    def tearDownClass(cls) -> None:
        sys.excepthook = cls.old_excepthook

    def test_message_handler(self) -> None:
        """Errors in message handlers should be passed back to qInfo and family."""

        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def qt_log(
                msg_type: QtMsgType, context: QMessageLogContext, msg: str
            ) -> None:
                raise MyException

            qInstallMessageHandler(qt_log)

            def quit_app() -> None:
                app.quit()

            err = None

            def test() -> None:
                nonlocal err
                try:
                    qInfo("test")
                except Exception as e:
                    err = e
                finally:
                    QTimer.singleShot(0, app, quit_app)

            QTimer.singleShot(0, app, test)

            app.exec()

            self.assertIsInstance(err, MyException)
            self.assertEqual([], self.unhandled)
        finally:
            shiboken6.delete(app)
            qInstallMessageHandler(None)

    def test_qtimer_single_shot(self) -> None:
        """QTimer.singleShot exceptions should be printed and cleared."""

        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            def throw_1() -> None:
                QTimer.singleShot(0, app, throw_2)
                raise MyException("1")

            def throw_2() -> None:
                QTimer.singleShot(0, app, throw_3)
                raise MyException("2")

            def throw_3() -> None:
                QTimer.singleShot(20, app, throw_4)
                raise MyException("3")

            def throw_4() -> None:
                QTimer.singleShot(0, app, quit_app)
                raise MyException("4")

            err = None

            def test() -> None:
                nonlocal err
                try:
                    QTimer.singleShot(0, app, throw_1)
                except Exception as e:
                    err = e

            QTimer.singleShot(0, app, test)
            QTimer.singleShot(2000, app, quit_app_fail)

            app.exec()

            self.assertFalse(fail)
            self.assertIsNone(err)
            self.assertEqual(4, len(self.unhandled))
            for exception in self.unhandled:
                self.assertIsInstance(exception, MyException)
        finally:
            shiboken6.delete(app)

    def test_qtimer_single_shot_exit(self) -> None:
        """QTimer.singleShot exceptions should be printed and cleared."""
        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            def throw() -> None:
                QTimer.singleShot(0, app, quit_app)
                raise MyException

            err = None

            def test() -> None:
                nonlocal err
                try:
                    QTimer.singleShot(0, app, throw)
                except Exception as e:
                    err = e

            QTimer.singleShot(0, app, test)
            QTimer.singleShot(2000, app, quit_app_fail)

            app.exec()

            self.assertFalse(fail)
            self.assertIsNone(err)
            self.assertEqual(1, len(self.unhandled))
            for exception in self.unhandled:
                self.assertIsInstance(exception, MyException)
        finally:
            shiboken6.delete(app)

    def test_qthread_start(self) -> None:
        """Errors in threads should be printed and cleared."""

        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                QThreadPool.globalInstance().waitForDone()
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            def throw() -> None:
                QTimer.singleShot(0, app, quit_app)
                raise MyException

            err = None

            def test() -> None:
                nonlocal err
                try:
                    QThreadPool.globalInstance().start(throw)
                except Exception as e:
                    err = e

            QTimer.singleShot(0, app, test)
            QTimer.singleShot(2000, app, quit_app_fail)

            app.exec()

            self.assertFalse(fail)
            self.assertIsNone(err)
            self.assertEqual(1, len(self.unhandled))
            for exception in self.unhandled:
                self.assertIsInstance(exception, MyException)
        finally:
            shiboken6.delete(app)

    def test_qrunnable_create(self) -> None:
        """Errors in QRunnable should be raised to the caller."""

        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            def throw() -> None:
                QTimer.singleShot(0, app, quit_app)
                raise MyException

            err = None
            runnable = QRunnable.create(throw)

            def test() -> None:
                nonlocal err
                try:
                    runnable.run()
                except Exception as e:
                    err = e

            QTimer.singleShot(0, app, test)
            QTimer.singleShot(2000, app, quit_app)

            app.exec()

            self.assertFalse(fail)
            self.assertIsInstance(err, MyException)
            self.assertEqual([], self.unhandled)
        finally:
            shiboken6.delete(app)

    def test_app_request_permission(self) -> None:
        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            class MyObj(QObject):
                def on_permission(self, permission) -> None:
                    QTimer.singleShot(0, app, quit_app)
                    raise MyException

            obj = MyObj()

            app.requestPermission(QCameraPermission(), obj, obj.on_permission)

            QTimer.singleShot(2000, app, quit_app_fail)

            app.exec()

            self.assertFalse(fail)
            self.assertEqual(1, len(self.unhandled))
            for exception in self.unhandled:
                self.assertIsInstance(exception, MyException)
        finally:
            shiboken6.delete(app)

    def test_app_request_permission2(self) -> None:
        app = QCoreApplication()

        try:
            self.unhandled.clear()

            def quit_app() -> None:
                app.quit()

            fail = False

            def quit_app_fail() -> None:
                nonlocal fail
                fail = True
                app.quit()

            class MyObj(QObject):
                def on_permission(self, permission) -> None:
                    QTimer.singleShot(0, app, quit_app)
                    raise MyException

            obj = MyObj()

            app.requestPermission(QCameraPermission(), obj, obj.on_permission)

            QTimer.singleShot(2000, app, quit_app_fail)

            app.exec()

            self.assertFalse(fail)
            self.assertEqual(1, len(self.unhandled))
            for exception in self.unhandled:
                self.assertIsInstance(exception, MyException)
        finally:
            shiboken6.delete(app)


if __name__ == "__main__":
    unittest.main()
