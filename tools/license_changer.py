#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
##
## $QT_BEGIN_LICENSE:COMM$
##
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## $QT_END_LICENSE$
##
#############################################################################

from argparse import ArgumentParser, RawTextHelpFormatter
import os
from pathlib import Path
import subprocess
import sys


DESC = """
Tool to adapt licenses to a commercial LTS branch
Requires the qtsdk/tqtc-qtsdk and qtqa repos to be checked out as siblings.
"""


REPO_DIR = Path(__file__).resolve().parents[1]


EXCLUSIONS = ['/build_scripts/', '/coin/', '/doc/', '/examples/',
              '/testing/', '/tests/',
              '/coin_build_instructions.py', '/coin_test_instructions.py',
              '/ez_setup.py', '/setup.py', '/testrunner.py']


if __name__ == '__main__':
    argument_parser = ArgumentParser(description=DESC,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument('--dry-run', '-d', action='store_true',
                                 help='Dry run, print commands')
    options = argument_parser.parse_args()
    dry_run = options.dry_run

    license_changer = (REPO_DIR.parent / 'tqtc-qtsdk' / 'packaging-tools'
                       / 'release_tools' / 'license_changer.pl')
    print('Checking ', license_changer)
    if not license_changer.is_file:
        print('Not found, please clone the qtsdk/tqtc-qtsdk repo')
        sys.exit(1)
    template = (REPO_DIR.parent / 'qtqa' / 'tests' / 'prebuild'
                / 'license' / 'templates' / 'header.COMM')
    print('Checking ', template)
    if not template.is_file():
        print('Not found, please clone the qtqa repo')
        sys.exit(1)

    os.chdir(REPO_DIR)
    fixed_cmd = [str(license_changer), '--path', str(REPO_DIR),
                 '--headerfile', str(template)]
    for e in EXCLUSIONS:
        fixed_cmd.append('--exclude')
        fixed_cmd.append(e)

    for license in ['GPL-EXCEPT', 'GPL', 'LGPL']:
        log = f'license_{license.lower()}_log.txt'
        cmd = fixed_cmd
        cmd.extend(['--replacehdr', license, '--errorlog', log])
        cmds = ' '.join(cmd)
        print('Running: ', cmds)
        if not dry_run:
            ex = subprocess.call(cmd)
            if ex != 0:
                print('FAIL! ', cmds)
                sys.exit(1)

    if not dry_run:
        subprocess.call(['git', 'diff'])
