#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for std::map container conversions'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import MapUser

class ExtendedMapUser(MapUser):
    def __init__(self):
        MapUser.__init__(self)
        self.create_map_called = False

    def createMap(self):
        self.create_map_called = True
        return {'two' : (complex(2.2, 2.2), 2),
                'three' : (complex(3.3, 3.3), 3),
                'five' : (complex(5.5, 5.5), 5),
                'seven' : (complex(7.7, 7.7), 7)}

class MapConversionTest(unittest.TestCase):
    '''Test case for std::map container conversions'''

    def testReimplementedVirtualMethodCall(self):
        '''Test if a Python override of a virtual method is correctly called from C++.'''
        mu = ExtendedMapUser()
        map_ = mu.callCreateMap()
        self.assertTrue(mu.create_map_called)
        self.assertEqual(type(map_), dict)
        for key, value in map_.items():
            self.assertEqual(type(key), str)
            self.assertEqual(type(value[0]), complex)
            self.assertEqual(type(value[1]), int)

    def testConversionInBothDirections(self):
        '''Test converting a map from Python to C++ and back again.'''
        mu = MapUser()
        map_ = {'odds' : [2, 4, 6], 'evens' : [3, 5, 7], 'primes' : [3, 4, 6]}
        mu.setMap(map_)
        result = mu.getMap()
        self.assertEqual(result, map_)

    def testConversionMapIntKeyValueTypeValue(self):
        '''C++ signature: MapUser::passMapIntValueType(const std::map<int, const ByteArray>&)'''
        mu = MapUser()
        map_ = {0 : 'string'}
        result = mu.passMapIntValueType(map_)
        self.assertEqual(map_, result)

if __name__ == '__main__':
    unittest.main()
