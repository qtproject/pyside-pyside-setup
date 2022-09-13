# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import fileinput
import re
import sys
from argparse import ArgumentParser, RawTextHelpFormatter


DESC="""Qhp file updater

Replaces virtual folder ids in .qhp files preparing for
registering the documentation in Qt Assistant."""


VIRTUAL_FOLDER_PATTERN = re.compile("(^.*virtualFolder.)doc(.*$)")
# Strip "PySide6.QtModule." from index entries
INDEX_CLASS_PATTERN = re.compile(r'^(\s*<keyword name=")PySide6\.[^.]+\.(.*\(class in .*)$')
INDEX_METHOD_PATTERN = re.compile(r'^(\s+<keyword name=".* \()PySide6\.[^.]+\.(.*>)$')


virtual_folder = ""
strip_pyside_module = False


def process_line(line):
    global virtual_folder
    match = VIRTUAL_FOLDER_PATTERN.match(line)
    if match:
        print(f"{match.group(1)}{virtual_folder}{match.group(2)}")
        return
    if strip_pyside_module:
        match = INDEX_METHOD_PATTERN.match(line)
        if match:
            print(f"{match.group(1)}{match.group(2)}")
            return
        match = INDEX_CLASS_PATTERN.match(line)
        if match:
            print(f"{match.group(1)}{match.group(2)}")
            return
    sys.stdout.write(line)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description=DESC,
                                formatter_class=RawTextHelpFormatter)
    arg_parser.add_argument('-v', '--vfolder', type=str,
                            help='String to be injected into the Qhp file.')
    arg_parser.add_argument("--pyside", "-p", action="store_true",
                            help="Strip the PySide module path off the index entries.")
    arg_parser.add_argument("file", type=str,  help='Qhp filename.')
    options = arg_parser.parse_args()
    virtual_folder = options.vfolder
    strip_pyside_module = options.pyside

    try:
        with fileinput.input(options.file, inplace=True,
                             backup=".bak") as fh:
            for line in fh:
                process_line(line)
    except Exception as e:
        print(f"WARNING: patch_qhp.py failed: {e}", file=sys.stderr)
