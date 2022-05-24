# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QMutex, QMutexLocker, QReadLocker, QReadWriteLock,
                            QThread, QWriteLocker)


class MyWriteThread(QThread):
    def __init__(self, lock):
        super().__init__()
        self.lock = lock
        self.started = False
        self.canQuit = False

    def run(self):
        self.started = True
        while not self.lock.tryLockForWrite():
            pass
        self.canQuit = True
        self.lock.unlock()


class MyReadThread(QThread):
    def __init__(self, lock):
        super().__init__()
        self.lock = lock
        self.started = False
        self.canQuit = False

    def run(self):
        self.started = True
        while not self.lock.tryLockForRead():
            pass
        self.canQuit = True
        self.lock.unlock()


class MyMutexedThread(QThread):
    def __init__(self, mutex):
        super().__init__()
        self.mutex = mutex
        self.started = False
        self.canQuit = False

    def run(self):
        self.started = True
        while not self.mutex.tryLock():
            pass
        self.mutex.unlock()
        self.canQuit = True


class TestQMutex (unittest.TestCase):

    def testReadLocker(self):
        lock = QReadWriteLock()
        thread = MyWriteThread(lock)

        with QReadLocker(lock):
            thread.start()
            while not thread.started:
                QThread.msleep(10)
            self.assertFalse(thread.canQuit)

        self.assertTrue(thread.wait(2000))
        self.assertTrue(thread.canQuit)

    def testWriteLocker(self):
        lock = QReadWriteLock()
        thread = MyReadThread(lock)

        with QWriteLocker(lock):
            thread.start()
            while not thread.started:
                QThread.msleep(10)
            self.assertFalse(thread.canQuit)

        self.assertTrue(thread.wait(2000))
        self.assertTrue(thread.canQuit)

    def testMutexLocker(self):
        mutex = QMutex()
        thread = MyMutexedThread(mutex)

        with QMutexLocker(mutex):
            thread.start()
            while not thread.started:
                QThread.msleep(10)
            self.assertFalse(thread.canQuit)

        self.assertTrue(thread.wait(2000))
        self.assertTrue(thread.canQuit)

    def testWithAsLocker(self):
        lock = QReadWriteLock()
        with QReadLocker(lock) as locker:
            self.assertTrue(isinstance(locker, QReadLocker))
        with QWriteLocker(lock) as locker:
            self.assertTrue(isinstance(locker, QWriteLocker))
        mutex = QMutex()
        with QMutexLocker(mutex) as locker:
            self.assertTrue(isinstance(locker, QMutexLocker))
        with self.assertRaises(TypeError):
            with QMutexLocker(lock) as locker:
                pass


if __name__ == '__main__':
    unittest.main()
