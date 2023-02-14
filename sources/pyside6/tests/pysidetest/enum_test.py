# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import Qt
from testbinding import Enum1, TestObjectWithoutNamespace

import dis

class ListConnectionTest(unittest.TestCase):

    def testEnumVisibility(self):
        self.assertEqual(Enum1.Option1, 1)
        self.assertEqual(Enum1.Option2, 2)
        self.assertEqual(TestObjectWithoutNamespace.Enum2.Option3, 3)
        self.assertEqual(TestObjectWithoutNamespace.Enum2.Option4, 4)

    def testFlagComparisonOperators(self):  # PYSIDE-1696, compare to self
        f1 = Qt.AlignHCenter | Qt.AlignBottom
        f2 = Qt.AlignHCenter | Qt.AlignBottom
        self.assertTrue(f1 == f1)
        self.assertTrue(f1 <= f1)
        self.assertTrue(f1 >= f1)
        self.assertFalse(f1 != f1)
        self.assertFalse(f1 < f1)
        self.assertFalse(f1 > f1)

        self.assertTrue(f1 == f2)
        self.assertTrue(f1 <= f2)
        self.assertTrue(f1 >= f2)
        self.assertFalse(f1 != f2)
        self.assertFalse(f1 < f2)
        self.assertFalse(f1 > f2)

        self.assertTrue(Qt.AlignHCenter < Qt.AlignBottom)
        self.assertFalse(Qt.AlignHCenter > Qt.AlignBottom)
        self.assertFalse(Qt.AlignBottom < Qt.AlignHCenter)
        self.assertTrue(Qt.AlignBottom > Qt.AlignHCenter)

# PYSIDE-1735: We are testing that opcodes do what they are supposed to do.
#              This is needed in the PyEnum forgiveness mode where we need
#              to introspect the code if an Enum was called with no args.
class InvestigateOpcodesTest(unittest.TestCase):

    def probe_function1(self):
        x = Qt.Alignment

    def probe_function2(self):
        x = Qt.Alignment()

    @staticmethod
    def read_code(func, **kw):
        return list(instr[:3] for instr in dis.Bytecode(func, **kw))

    @staticmethod
    def get_sizes(func, **kw):
        ops = list((instr.opname, instr.offset) for instr in dis.Bytecode(func, **kw))
        res = []
        for idx in range(1, len(ops)):
            res.append((ops[idx - 1][0], ops[idx][1] - ops[idx - 1][1]))
        return sorted(res, key=lambda x: (x[1], x[0]))

    _sin = sys.implementation.name
    @unittest.skipIf(hasattr(sys.flags, "nogil"), f"{_sin} has different opcodes")
    def testByteCode(self):
        import dis
        # opname, opcode, arg
        result_1 = [('LOAD_GLOBAL', 116, 0),
                    ('LOAD_ATTR',   106, 1),
                    ('STORE_FAST',  125, 1),
                    ('LOAD_CONST',  100, 0),
                    ('RETURN_VALUE', 83, None)]

        result_2 = [('LOAD_GLOBAL', 116, 0),
                    ('LOAD_METHOD', 160, 1),
                    ('CALL_METHOD', 161, 0),
                    ('STORE_FAST',  125, 1),
                    ('LOAD_CONST',  100, 0),
                    ('RETURN_VALUE', 83, None)]

        if sys.version_info[:2] <= (3, 6):

            result_2 = [('LOAD_GLOBAL',   116, 0),
                        ('LOAD_ATTR',     106, 1),
                        ('CALL_FUNCTION', 131, 0),
                        ('STORE_FAST',    125, 1),
                        ('LOAD_CONST',    100, 0),
                        ('RETURN_VALUE',   83, None)]

        if sys.version_info[:2] == (3, 11):
            # Note: Python 3.11 is a bit more complex because it can optimize itself.
            # Opcodes are a bit different, and a hidden second code object is used.
            # We investigate this a bit, because we want to be warned when things change.
            QUICKENING_WARMUP_DELAY = 8

            result_1 = [('RESUME',      151, 0),
                        ('LOAD_GLOBAL', 116, 0),
                        ('LOAD_ATTR',   106, 1),
                        ('STORE_FAST',  125, 1),
                        ('LOAD_CONST',  100, 0),
                        ('RETURN_VALUE', 83, None)]

            result_2 = [('RESUME',      151, 0),
                        ('LOAD_GLOBAL', 116, 1),
                        ('LOAD_ATTR',   106, 1),
                        ('PRECALL',     166, 0),
                        ('CALL',        171, 0),
                        ('STORE_FAST',  125, 1),
                        ('LOAD_CONST',  100, 0),
                        ('RETURN_VALUE', 83, None)]

            sizes_2 = [('LOAD_CONST',   2),
                       ('RESUME',       2),
                       ('STORE_FAST',   2),
                       ('PRECALL',      4),
                       ('CALL',        10),
                       ('LOAD_ATTR',   10),
                       ('LOAD_GLOBAL', 12)]

            self.assertEqual(self.read_code(self.probe_function2, adaptive=True), result_2)
            self.assertEqual(self.get_sizes(self.probe_function2, adaptive=True), sizes_2)

            @staticmethod
            def code_quicken(f, times):
                # running the code triggers acceleration after some runs.
                for _ in range(times):
                    f()

            code_quicken(self.probe_function2, QUICKENING_WARMUP_DELAY-1)
            self.assertEqual(self.read_code(self.probe_function2, adaptive=True), result_2)
            self.assertEqual(self.get_sizes(self.probe_function2, adaptive=True), sizes_2)

            result_3 = [('RESUME_QUICK',       150, 0),
                        ('LOAD_GLOBAL_MODULE',  55, 1),
                        ('LOAD_ATTR_ADAPTIVE',  39, 1),
                        ('PRECALL_ADAPTIVE',    64, 0),
                        ('CALL_ADAPTIVE',       22, 0),
                        ('STORE_FAST',         125, 1),
                        ('LOAD_CONST',         100, 0),
                        ('RETURN_VALUE',        83, None)]

            sizes_3 = [('LOAD_CONST',          2),
                       ('RESUME_QUICK',        2),
                       ('STORE_FAST',          2),
                       ('PRECALL_ADAPTIVE',    4),
                       ('CALL_ADAPTIVE',      10),
                       ('LOAD_ATTR_ADAPTIVE', 10),
                       ('LOAD_GLOBAL_MODULE', 12)]

            code_quicken(self.probe_function2, 1)
            self.assertEqual(self.read_code(self.probe_function2, adaptive=True), result_3)
            self.assertEqual(self.get_sizes(self.probe_function2, adaptive=True), sizes_3)

        if sys.version_info[:2] >= (3, 12):

            result_1 = [('RESUME', 151, 0),
                        ('LOAD_GLOBAL', 116, 0),
                        ('LOAD_ATTR', 106, 2),
                        ('STORE_FAST', 125, 1),
                        ('RETURN_CONST', 121, 0)]

            result_2 = [('RESUME', 151, 0),
                        ('LOAD_GLOBAL', 116, 1),
                        ('LOAD_ATTR', 106, 2),
                        ('CALL', 171, 0),
                        ('STORE_FAST', 125, 1),
                        ('RETURN_CONST', 121, 0)]


        self.assertEqual(self.read_code(self.probe_function1), result_1)
        self.assertEqual(self.read_code(self.probe_function2), result_2)


if __name__ == '__main__':
    unittest.main()

