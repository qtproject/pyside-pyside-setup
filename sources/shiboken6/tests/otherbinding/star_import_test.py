#!/usr/bin/env python
# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""PYSIDE-2404: Test whether star imports work as they require special handling
   by the lazy initialization."""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

SHIBOKEN_NAME = "shiboken6.Shiboken"
MINIMAL_NAME = "minimal"
OTHER_NAME = "other"

shiboken_loaded = 1 if sys.modules.get(SHIBOKEN_NAME) else 0
minimal_loaded = 1 if sys.modules.get(MINIMAL_NAME) else 0
other_loaded = 1 if sys.modules.get(OTHER_NAME) else 0

from minimal import *       # noqa: F403

shiboken_loaded += 2 if sys.modules.get(SHIBOKEN_NAME) else 0
minimal_loaded += 2 if sys.modules.get(MINIMAL_NAME) else 0
other_loaded += 2 if sys.modules.get(OTHER_NAME) else 0

from other import Number    # noqa: F403
from other import *         # noqa: F403

shiboken_loaded += 4 if sys.modules.get(SHIBOKEN_NAME) else 0
minimal_loaded += 4 if sys.modules.get(MINIMAL_NAME) else 0
other_loaded = +4 if sys.modules.get(OTHER_NAME) else 0

import shiboken6.Shiboken   # noqa: F401 F403

shiboken_loaded += 8 if sys.modules.get(SHIBOKEN_NAME) else 0


class ValTest(unittest.TestCase):

    def test(self):
        val_id = 123
        val = Val(val_id)  # noqa: F405
        self.assertEqual(val.valId(), val_id)


class Simple(Number):

    def __init__(self):
        Number.__init__(self, 42)


class OtherTest(unittest.TestCase):

    def testConstructor(self):
        o = Simple()
        self.assertTrue(isinstance(o, Number))


class StarImportTest(unittest.TestCase):
    """
    This test is meant for Lazy Init.
    We explicitly choose modules which are able to lazy load.

    The ValTest:
    ------------
    We load something with `import *`.
    There is no module from our known ones imported.
    This means we need stack introspection to find out that this was
    a star import and we must disable lazyness.

    The OtherTest:
    --------------
    We load something normally that should be lazy.
    After that, we follow with a star import.
    Now the stack introspection does not work, because the loading is
    cached. The first import did a lazy load. The following star import
    needs to undo the lazyness. But now we have a redirected import.

    All tests simply check if the objects are real and not just names.
    The <module>_loaded tests prevend upcoming internal dependencies.

    To make sure that Shiboken is really not involved, it is checked
    and really imported afterwards (ensuring nothing is misspelled).
    """

    def testStar(self):
        self.assertEqual(other_loaded, 4)
        self.assertEqual(minimal_loaded, 6)
        self.assertEqual(shiboken_loaded, 14)
        # Interesting effect: Did not expect that shiboken is loaded at all.


if __name__ == '__main__':
    unittest.main()
