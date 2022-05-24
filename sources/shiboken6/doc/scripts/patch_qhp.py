# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import fileinput
import re
from argparse import ArgumentParser, RawTextHelpFormatter

options = ArgumentParser(description='Qhp file updater',
                         formatter_class=RawTextHelpFormatter)
options.add_argument('-f',
                     '--filename',
                     type=str,
                     help='Qhp filename with the relative path.',
                     required=True)
options.add_argument('-v',
                     '--vfolder',
                     type=str,
                     help='String to be injected into the Qhp file.')
args=options.parse_args()

try:
    for line in fileinput.input(args.filename,inplace=True,backup='.bak'):
        line_copy=line.strip()
        if not line_copy: # check for empty line
            continue
        match=re.match('(^.*virtualFolder.)doc(.*$)',line)
        if match:
            repl=''.join([match.group(1), args.vfolder, match.group(2)])
            print(line.replace(match.group(0),repl),end=' ')
        else:
            print(line.rstrip())
except:
    pass
