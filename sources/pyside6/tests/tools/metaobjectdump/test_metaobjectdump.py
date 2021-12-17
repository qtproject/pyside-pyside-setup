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
import subprocess
import unittest

from pathlib import Path

"""Test for pyside6-metaobjectdump.

The test prints commands to regenerate the base line."""


def msg_regenerate(cmd, baseline):
    cmd_str = " ".join(cmd)
    return (f"# Regenerate {baseline}\n"
            f"{cmd_str} > {baseline}")


@unittest.skipIf(sys.version_info < (3, 8), "Needs a recent ast module")
class TestMetaObjectDump(unittest.TestCase):
    """Test for the metaobjectdump tool. Compares the output of metaobjectdump.py for some
       example files in compact format."""

    def setUp(self):
        super().setUp()
        self._dir = Path(__file__).parent.resolve()
        pyside_root = self._dir.parents[4]
        self._metaobjectdump_tool = pyside_root / "sources" / "pyside-tools" / "metaobjectdump.py"
        self._examples_dir = (pyside_root / "examples" /
                              "declarative" / "referenceexamples")

        # Compile a list of examples (tuple [file, base line, command])
        examples = []
        for d in ["coercion", "default"]:
            example_dir = self._examples_dir / d
            examples.append(example_dir / "birthdayparty.py")
            examples.append(example_dir / "person.py")

        metaobjectdump_cmd_root = [sys.executable, os.fspath(self._metaobjectdump_tool), "-c", "-s"]
        self._examples = []
        for example in examples:
            name = example.parent.name
            baseline_name = f"baseline_{name}_{example.stem}.json"
            baseline_path = self._dir / baseline_name
            cmd = metaobjectdump_cmd_root + [os.fspath(example)]
            self._examples.append((example, baseline_path, cmd))
            print(msg_regenerate(cmd, baseline_path))

    def testMetaObjectDump(self):
        self.assertTrue(self._examples_dir.is_dir())
        self.assertTrue(self._metaobjectdump_tool.is_file())

        for example, baseline, cmd in self._examples:
            self.assertTrue(example.is_file())
            self.assertTrue(baseline.is_file())
            baseline_data = baseline.read_text()

            popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            actual = popen.communicate()[0].decode("UTF-8")
            self.assertEqual(popen.returncode, 0)
            self.assertEqual(baseline_data, actual)


if __name__ == '__main__':
    unittest.main()
