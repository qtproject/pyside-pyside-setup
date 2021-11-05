# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import ContainerTest


EXPECTED_DICT = {1: ["v1"], 2: ["v2_1", "v2_2"],
                 3: ["v3"],
                 4: ["v4_1", "v4_2"]}


EXPECTED_LIST = [1, 2]


def sort_values(m):
    """Sort value lists in dicts since passing through a QMultiMap changes the order"""
    result = {}
    for key, values in m.items():
        result[key] = sorted(values)
    return result


class ContainerTestTest(unittest.TestCase):

    def testMultiMap(self):
        m1 = ContainerTest.createMultiMap()
        self.assertEqual(sort_values(m1), EXPECTED_DICT)
        m2 = ContainerTest.passThroughMultiMap(m1)
        self.assertEqual(sort_values(m2), EXPECTED_DICT)

    def testMultiHash(self):
        m1 = ContainerTest.createMultiHash()
        self.assertEqual(sort_values(m1), EXPECTED_DICT)
        m2 = ContainerTest.passThroughMultiHash(m1)
        self.assertEqual(sort_values(m2), EXPECTED_DICT)

    def testList(self):
        l1 = ContainerTest.createList();
        self.assertEqual(l1, EXPECTED_LIST)
        l2 = ContainerTest.passThroughList(l1)
        self.assertEqual(l2, EXPECTED_LIST)

    def testSet(self):
        # FIXME PYSIDE 7: A PySet should be returned from QSet (currently PyList)
        s1 = set(ContainerTest.createSet());  # Order is not predictable
        s2 = set(ContainerTest.passThroughSet(s1))
        self.assertEqual(sorted(list(s1)), sorted(list(s2)))

        # Since lists are iterable, it should be possible to pass them to set API
        l2 = ContainerTest.passThroughSet(EXPECTED_LIST)
        self.assertEqual(sorted(l2), EXPECTED_LIST)


if __name__ == '__main__':
    unittest.main()
