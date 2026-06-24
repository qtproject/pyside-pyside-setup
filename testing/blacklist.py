# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""
testing/blacklist.py

Take a blacklist file and build classifiers for all tests.

find_matching_line() adds info using classifiers.
"""

from .buildlog import builds
from .helper import decorate


class BlackList:
    def __init__(self, blname):
        if blname:
            with open(blname) as f:
                self.raw_data = f.readlines()
        else:
            self.raw_data = []

        def filtered_line(line):
            if "#" in line:
                line = line[:line.index("#")]
            return line.split()

        # now put every bracketed line in a test
        # and use subsequent identifiers for a match
        def is_test(fline):
            return fline and fline[0].startswith("[")

        self.tests = {}
        name = None
        for line in self.raw_data:
            fline = filtered_line(line)
            if is_test(fline):
                # a new name
                name = decorate(fline[0][1:-1])
                # Allow for repeated sections
                self.tests.setdefault(name, [])
            elif fline:
                if name is None:
                    # global section: entries before any [section] header
                    name = ""
                    self.tests[""] = []
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
        thing = mod_name if mod_name in self.tests else decorate(mod_name)
        if thing not in self.tests:
            return None
        for line in self.tests[thing]:
            keys = set(line)
            if keys <= classifiers:
                # found a match!
                return line
