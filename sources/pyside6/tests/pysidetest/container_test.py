# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
        s1 = ContainerTest.createSet();  # Order is not predictable
        s2 = ContainerTest.passThroughSet(s1)
        self.assertEqual(sorted(list(s1)), sorted(list(s2)))

        # Since lists are iterable, it should be possible to pass them to set API
        l2 = ContainerTest.passThroughSet(EXPECTED_LIST)
        self.assertEqual(sorted(list(l2)), EXPECTED_LIST)


if __name__ == '__main__':
    unittest.main()
