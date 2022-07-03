#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for renaming using target-lang-name attribute.'''

import os
import re
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import RenamedValue, RenamedUser

from shiboken6 import Shiboken

from shibokensupport.signature import get_signature


class RenamingTest(unittest.TestCase):
    def test(self):
        '''Tests whether the C++ class ToBeRenamedValue renamed via attribute
           target-lang-name to RenamedValue shows up in consuming function
           signature strings correctly.
        '''
        renamed_value = RenamedValue()
        self.assertEqual(str(type(renamed_value)),
                         "<class 'sample.RenamedValue'>")
        rename_user = RenamedUser()
        rename_user.useRenamedValue(renamed_value)
        actual_signature = str(get_signature(rename_user.useRenamedValue))
        self.assertTrue(re.match(r"^\(self,\s*?v:\s*?sample.RenamedValue\)\s*?->\s*?None$",
                                 actual_signature))



if __name__ == '__main__':
    unittest.main()
