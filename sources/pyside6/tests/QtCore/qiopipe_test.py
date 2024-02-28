# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for the QIOPipe class'''

from PySide6.QtCore import QIODevice, QIOPipe

import unittest


class QIOPipeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pipe = QIOPipe()
        self.pipe.open(QIODevice.OpenModeFlag.ReadWrite)
        return super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def ready_read_bytes_written(self):
        received_data = self.pipe.end2().readAll().data()
        self.assertEqual(received_data, self.data)

    def test_readyRead(self):
        self.data = b"Hello, World!"
        self.pipe.end2().readyRead.connect(self.ready_read_bytes_written)
        self.pipe.end1().write(self.data)

    def test_bytesWritten(self):
        self.data = b"Hello, World!"
        self.pipe.end2().bytesWritten.connect(self.ready_read_bytes_written)
        self.pipe.end1().write(self.data)


if __name__ == '__main__':
    unittest.main()
