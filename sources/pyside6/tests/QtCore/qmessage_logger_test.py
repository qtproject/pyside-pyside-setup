# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import unittest
import logging
import io
import sys
import os

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QMessageLogger, QLoggingCategory, QtMsgType


class QtMessageHandler(logging.Handler):
    def __init__(self, category):
        super().__init__()
        self.category = category

    def emit(self, record):
        log_entry = self.format(record)
        logger = QMessageLogger(__file__, record.lineno, record.funcName)

        if record.levelno == logging.DEBUG:
            if self.category.isDebugEnabled():
                logger.debug(self.category, log_entry)
            else:
                logger.debug(log_entry)


class TestQMessageLogger(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_qmessagelogger")
        self.logger.setLevel(logging.DEBUG)
        self.stream = io.StringIO()
        self.capture_handler = logging.StreamHandler(self.stream)
        self.capture_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.capture_handler)

    def tearDown(self):
        self.logger.removeHandler(self.capture_handler)

    def test_debug_with_category_enabled(self):
        category_enabled = QLoggingCategory("test.category.enabled")
        # 0 is QtDebugMsg
        category_enabled.setEnabled(QtMsgType.QtDebugMsg, True)

        qt_handler_enabled = QtMessageHandler(category_enabled)
        self.logger.addHandler(qt_handler_enabled)

        self.logger.debug("Debug with category enabled")
        self.logger.removeHandler(qt_handler_enabled)

        captured = self.stream.getvalue()
        self.assertIn("Debug with category enabled", captured)

    def test_debug_with_category_disabled(self):
        category_disabled = QLoggingCategory("test.category.disabled")

        qt_handler_disabled = QtMessageHandler(category_disabled)
        self.logger.addHandler(qt_handler_disabled)

        self.logger.debug("Debug with category disabled")
        self.logger.removeHandler(qt_handler_disabled)

        captured = self.stream.getvalue()
        self.assertIn("Debug with category disabled", captured)


if __name__ == "__main__":
    unittest.main()
