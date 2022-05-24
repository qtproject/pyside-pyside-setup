# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for Positioning'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtPositioning import QGeoPositionInfoSource


class QPositioningTestCase(unittest.TestCase):
    def test(self):
        source = QGeoPositionInfoSource.createDefaultSource(None)
        self.assertTrue(source is not None)
        name = source.sourceName()
        print(f"QtPositioning source: {name}")
        self.assertTrue(name)


if __name__ == "__main__":
    unittest.main()
