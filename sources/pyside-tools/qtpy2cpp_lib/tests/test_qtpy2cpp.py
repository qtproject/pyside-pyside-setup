# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import subprocess
import tempfile
import sys
from pathlib import Path

# run pytest-3


def diff_code(actual_code, expected_file):
    """Helper to run diff if something fails (Linux only)."""
    with tempfile.NamedTemporaryFile(suffix=".cpp") as tf:
        tf.write(actual_code.encode('utf-8'))
        tf.flush()
        diff_cmd = ["diff", "-u", expected_file, tf.name]
        subprocess.run(diff_cmd)


def run_converter(tool, file):
    """Run the converter and return C++ code generated from file."""
    cmd = [sys.executable, tool, "--stdout", file]
    output = ""
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        output_b, errors_b = proc.communicate()
        output = output_b.decode('utf-8')
        if errors_b:
            print(errors_b.decode('utf-8'), file=sys.stderr)
    return output


def test_examples():
    dir = Path(__file__).resolve().parent
    tool = dir.parents[1] / "qtpy2cpp.py"
    assert tool.is_file
    for test_file in (dir / "baseline").glob("*.py"):
        assert test_file.is_file
        expected_file = test_file.parent / (test_file.stem + ".cpp")
        if expected_file.is_file():
            actual_code = run_converter(tool, test_file)
            assert actual_code
            expected_code = expected_file.read_text()
            # Strip the license
            code_start = expected_code.find("// Converted from")
            assert code_start != -1
            expected_code = expected_code[code_start:]

            if actual_code != expected_code:
                diff_code(actual_code, expected_file)
            assert actual_code == expected_code
        else:
            print(f"Warning, {test_file} is missing a .cpp file.",
                  file=sys.stderr)
