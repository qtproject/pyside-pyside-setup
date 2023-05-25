#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import re
import subprocess
import sys
import tempfile
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent
from typing import Optional, Tuple


VERSION = 2


DESC = """Runs uic on a set of UI files and displays the resulting widgets."""


TEMP_DIR = Path(tempfile.gettempdir())


def get_class_name(file: Path) -> Tuple[Optional[str], Optional[str]]:
    """Return class name and widget name of UI file."""
    pattern = re.compile('^\s*<widget class="(\w+)" name="(\w+)"\s*>.*$')
    for l in Path(file).read_text().splitlines():
        match = pattern.match(l)
        if match:
            return (match.group(1), match.group(2))
    return (None, None)


def test_file(file: str, uic: bool=False) -> bool:
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
            sys.exit(app.exec_())''')
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
