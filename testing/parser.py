# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import re
from collections import namedtuple
from io import StringIO

"""
testing/parser.py

Parse test output lines from ctest and build TestResult objects.

TestParser.iter_blacklist adds info from the blacklist while iterating
over the test results.
"""

_EXAMPLE = """
Example output:

ip1 n        sharp mod_name                                            code      tim
-----------------------------------------------------------------------------------------
114/391 Test #114: QtCore_qfileinfo_test-42 ........................   Passed    0.10 sec
        Start 115: QtCore_qfile_test
115/391 Test #115: QtCore_qfile_test ...............................***Failed    0.11 sec
        Start 116: QtCore_qflags_test

We will only look for the dotted lines and calculate everything from that.
The summary statistics at the end will be ignored. That allows us to test
this functionality with short timeout values.

Note the field "mod_name". I had split this before, but it is necessary
to use the combination as the key, because the test names are not unique.
"""

_TEST_PAT_PRE = r"""
    ^                          # start
    \s*                        # any whitespace ==: WS
    ([0-9]+)/([0-9]+)          #                         ip1 "/" n
    \s+                        # some WS
    Test                       #                         "Test"
    \s+                        # some WS
    \#                         # sharp symbol            "#"
    ([0-9]+)                   #                         sharp
    :                          # colon symbol            ':'
    """
_TEST_PAT = (
    _TEST_PAT_PRE
    + r"""
    \s+                        # some WS
    ([\w-]+)                   #                         mod_name
    .*?                        # whatever (non greedy)
    (                          #
      (Passed)                 # either "Passed", None
      |                        #
      \*\*\*(\w+.*?)           # or     None, "Something"
    )                          #                         code
    \s+                        # some WS
    ([0-9]+\.[0-9]+)           #                         tim
    \s+                        # some WS
    sec                        #                         "sec"
    \s*                        # any WS
    $                          # end
    """
)

# validation of our pattern:
assert re.match(_TEST_PAT, _EXAMPLE.splitlines()[5], re.VERBOSE)
assert len(re.match(_TEST_PAT, _EXAMPLE.splitlines()[5], re.VERBOSE).groups()) == 8
assert len(re.match(_TEST_PAT, _EXAMPLE.splitlines()[7], re.VERBOSE).groups()) == 8

TestResult = namedtuple(
    "TestResult", "idx n sharp mod_name passed " "code time fatal rich_result".split()
)


def _parse_tests(test_log):
    """
    Create a TestResult object for every entry.
    """
    result = []
    if isinstance(test_log, StringIO):
        lines = test_log.readlines()
    elif test_log is not None and os.path.exists(test_log):
        with open(test_log) as f:
            lines = f.readlines()
    else:
        lines = []

    # PYSIDE-1229: Fix disrupted lines like "Exit code 0xc0000409\n***Exception:"
    pat = _TEST_PAT_PRE
    for idx, line in enumerate(lines[:-1]):
        match = re.match(pat, line, re.VERBOSE)
        if match and line.split()[-1] != "sec":
            # don't change the number of lines
            lines[idx:idx + 2] = [line.rstrip() + lines[idx + 1], ""]

    pat = _TEST_PAT
    for line in lines:
        match = re.match(pat, line, re.VERBOSE)
        if match:
            idx, n, sharp, mod_name, much_stuff, code1, code2, tim = match.groups()
            # either code1 or code2 is None
            code = code1 or code2
            idx, n, sharp, code, tim = int(idx), int(n), int(sharp), code.lower(), float(tim)
            item = TestResult(idx, n, sharp, mod_name, code == "passed", code, tim, False, None)
            result.append(item)

    # PYSIDE-1229: Be sure that the numbering of the tests is consecutive
    for idx, item in enumerate(result):
        # testing fatal error:
        # Use "if idx + 1 != item.idx or idx == 42:"
        if idx + 1 != item.idx:
            # The numbering is disrupted. Provoke an error in this line!
            code = f"{code}, but lines are disrupted!"
            result[idx] = item._replace(
                passed=False, code=f"{item.code}, but lines are disrupted!", fatal=True
            )
            break
    return result


class TestParser(object):
    def __init__(self, test_log):
        self._results = _parse_tests(test_log)

    @property
    def results(self):
        return self._results

    def __len__(self):
        return len(self._results)

    def iter_blacklist(self, blacklist):
        bl = blacklist
        for item in self.results:
            passed = item.passed
            match = bl.find_matching_line(item)
            if not passed:
                if match:
                    res = "BFAIL"
                else:
                    res = "FAIL!"
            else:
                if match:
                    res = "BPASS"
                else:
                    res = "PASS"
            if item.fatal:
                # PYSIDE-1229: Stop the testing completely when a fatal error exists
                res = "FATAL"
            yield item._replace(rich_result=res)
