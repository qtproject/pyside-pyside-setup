#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
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
