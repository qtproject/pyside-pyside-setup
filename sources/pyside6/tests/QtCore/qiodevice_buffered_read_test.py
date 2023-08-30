# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for buffered read methods of QIODevice'''

from PySide6.QtCore import QBuffer

import enum
import unittest


class TestQIODeviceBufferedRead(unittest.TestCase):
    class TestType(enum.Enum):
        Read = enum.auto()
        ReadLine = enum.auto()
        Peek = enum.auto()

    def setUp(self) -> None:
        self.buffer = QBuffer()
        self.text = "Tomato juice\nPotato salad\n"

        self.assertTrue(
            self.buffer.open(QBuffer.OpenModeFlag.ReadWrite), self.buffer.errorString())
        self.assertGreaterEqual(
            self.buffer.write(self.text.encode("utf-8")), 0, self.buffer.errorString())

        self.buffer.seek(0)

    def tearDown(self) -> None:
        self.buffer.close()

    def test_read(self) -> None:
        response1 = self.buffer.read(1024).data().decode("utf-8")
        self.assertEqual(response1, self.text)

        self.buffer.seek(0)
        response2 = bytearray(1024)
        bytes_read = self.buffer.read(response2, 1024)

        self.assertGreaterEqual(bytes_read, 0, self.buffer.errorString())
        self.assertEqual(response2[:bytes_read].decode("utf-8"), response1)

    def test_readLine(self) -> None:
        response1 = self.buffer.readLine(1024).data().decode("utf-8")
        # Only read until the first line (including the line break)
        self.assertEqual(response1, self.text.split("\n", 1)[0] + "\n")

        self.buffer.seek(0)
        response2 = bytearray(1024)
        bytes_read = self.buffer.readLine(response2, 1024)

        self.assertGreaterEqual(bytes_read, 0, self.buffer.errorString())
        self.assertEqual(response2[:bytes_read].decode("utf-8"), response1)

    def test_peek(self) -> None:
        response1 = self.buffer.peek(1024).data().decode("utf-8")
        self.assertEqual(response1, self.text)

        # Test that peek has no side effects
        response_again1 = self.buffer.read(1024).data().decode("utf-8")
        self.assertEqual(response_again1, response1)

        self.buffer.seek(0)
        response2 = bytearray(1024)
        bytes_read = self.buffer.peek(response2, 1024)

        self.assertGreaterEqual(bytes_read, 0, self.buffer.errorString())
        self.assertEqual(response2[:bytes_read].decode("utf-8"), response1)

        # Test that peek has no side effects
        response_again2 = bytearray(1024)
        bytes_read_again2 = self.buffer.read(response_again2, 1024)
        self.assertEqual(bytes_read, bytes_read_again2)
        self.assertEqual(response_again2, response2)


if __name__ == "__main__":
    unittest.main()
