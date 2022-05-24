# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import re
import subprocess
import sys
import tempfile
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent
from typing import Optional, Tuple

VERSION = 6


DESC = """Runs uic on a set of UI files and displays the resulting widgets."""


TEMP_DIR = Path(tempfile.gettempdir())


def get_class_name(file: Path) -> Tuple[Optional[str], Optional[str]]:
    """Return class name and widget name of UI file."""
    pattern = re.compile(r'^\s*<widget class="(\w+)" name="(\w+)"\s*>.*$')
    for line in Path(file).read_text().splitlines():
        match = pattern.match(line)
        if match:
            return (match.group(1), match.group(2))
    return (None, None)


def test_file(file: str, uic: bool = False) -> bool:
    """Run uic on a UI file and show the resulting UI."""
    path = Path(file)
    (klass, name) = get_class_name(path)
    if not klass:
        print(f'{file} does not appear to be a UI file', file=sys.stderr)
        return False
    py_klass = f'Ui_{name}'
    py_file_basename = py_klass.lower()
    py_file = TEMP_DIR / (py_file_basename + '.py')
    py_main = TEMP_DIR / 'main.py'
    cmd = ['uic', '-g', 'python'] if uic else [f'pyside{VERSION}-uic']
    cmd.extend(['-o', os.fspath(py_file), file])
    try:
        subprocess.call(cmd)
    except FileNotFoundError as e:
        print(str(e) + " (try -u for uic)", file=sys.stderr)
        return False
    main_source = dedent(f'''\
        import sys
        from PySide{VERSION}.QtWidgets import QApplication, {klass}
        from {py_file_basename} import {py_klass}

        if __name__ == "__main__":
            app = QApplication(sys.argv)
            ui = {py_klass}()
            widget = {klass}()
            ui.setupUi(widget)
            widget.show()
            sys.exit(app.exec())''')
    py_main.write_text(main_source)
    exit_code = subprocess.call([sys.executable, os.fspath(py_main)])
    py_main.unlink()
    py_file.unlink()
    return exit_code == 0


if __name__ == '__main__':
    argument_parser = ArgumentParser(description=DESC,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument('--uic', '-u', action='store_true',
                                 help='Use uic instead of pyside-uic')
    argument_parser.add_argument("files", help="UI Files",
                                 nargs='+', type=str)
    options = argument_parser.parse_args()
    failed = 0
    count = len(options.files)
    for i, file in enumerate(options.files):
        print(f'{i+1}/{count} {file}')
        if not test_file(file, options.uic):
            failed += 1
    if failed != 0:
        print(f'{failed}/{count} failed.')
    sys.exit(failed)
