# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
testing/blacklist.py

Take a blacklist file and build classifiers for all tests.

find_matching_line() adds info using classifiers.
"""

from io import StringIO

from .buildlog import builds
from .helper import decorate


class BlackList(object):
    def __init__(self, blname):
        if not blname:
            f = StringIO()
            self.raw_data = []
        else:
            with open(blname) as f:
                self.raw_data = f.readlines()
        # keep all lines, but see what is not relevant
        lines = self.raw_data[:]

        def filtered_line(line):
            if "#" in line:
                line = line[:line.index("#")]
            return line.split()

        # now put every bracketed line in a test
        # and use subsequent identifiers for a match
        def is_test(fline):
            return fline and fline[0].startswith("[")

        self.tests = {}

        if not lines:
            # nothing supplied
            return

        for idx, line in enumerate(lines):
            fline = filtered_line(line)
            if not fline:
                continue
            if is_test(fline):
                break
            # we have a global section
            name = ""
            self.tests[name] = []
        for idx, line in enumerate(lines):
            fline = filtered_line(line)
            if is_test(fline):
                # a new name
                name = decorate(fline[0][1:-1])
                # Allow for repeated sections
                self.tests.setdefault(name, [])
            elif fline:
                # a known name with a new entry
                self.tests[name].append(fline)

    def find_matching_line(self, test):
        """
        Take a test result.
        Find a line in the according blacklist file where all keys of the line are found.
        If line not found, do nothing.
        if line found and test passed, it is a BPASS.
        If line found and test failed, it is a BFAIL.
        """
        classifiers = set(builds.classifiers)

        if "" in self.tests:
            # this is a global section
            for line in self.tests[""]:
                keys = set(line)
                if keys <= classifiers:
                    # found a match!
                    return line
        mod_name = test.mod_name
        if mod_name not in self.tests and decorate(mod_name) not in self.tests:
            return None
        if mod_name in self.tests:
            thing = mod_name
        else:
            thing = decorate(mod_name)
        for line in self.tests[thing]:
            keys = set(line)
            if keys <= classifiers:
                # found a match!
                return line
        else:
            return None  # nothing found
