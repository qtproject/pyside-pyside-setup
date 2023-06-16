# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
Tool to run qtattributionsscanner and convert its output to rst
"""

import os
import json
import subprocess
import sys
import warnings
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path


USAGE = "Usage: qtattributionsscannertorst [directory] [file]'"


libexec_dir = None


def indent(lines, indent):
    result = ''
    for l in lines:
        result = f"{result}{indent}{l}\n"
    return result


rstHeader = """Licenses Used in Qt for Python
******************************

Qt for Python contains some code that is not provided under the
GNU Lesser General Public License (LGPL) or the Qt Commercial License,
but rather under specific licenses from the original authors.
The Qt Company gratefully acknowledges these and other contributions
to Qt for Python. We recommend that programs that use Qt for Python
also acknowledge these contributions, and quote these license
statements in an appendix to the documentation.

Note: You only need to comply with (and acknowledge) the licenses of
the third-party components that you are using with your application.
Click the name of the component to see the licensing details.

Third-party Licenses
^^^^^^^^^^^^^^^^^^^^

The licenses for the third-party sources used by Qt itself are listed
in
`Qt documentation <https://doc.qt.io/qt-5/licenses-used-in-qt.html>`_.
The following table lists parts of Qt for Python that incorporates
code licensed under third-party opensource licenses:

"""


def rstHeadline(title):
    return f"{title}\n{'-' * len(title)}\n"


def rstUrl(title, url):
    return f"`{title} <{url}>`_"


def rstLiteralBlock(lines):
    return f"::\n\n{indent(lines, '    ')}\n\n"


def rstLiteralBlockFromText(text):
    return rstLiteralBlock(text.strip().split('\n'))


def readFile(fileName):
    with open(fileName, 'r') as file:
        return file.readlines()


def get_libexec_dir():
    libexec_b = subprocess.check_output("qtpaths6 -query QT_INSTALL_LIBEXECS", shell=True)
    return libexec_b.decode('utf-8').strip()


def runScanner(directory, targetFileName, libexec_dir):
    # qtattributionsscanner recursively searches for qt_attribution.json files
    # and outputs them in JSON with the paths of the 'LicenseFile' made absolute
    scanner = os.path.join(libexec_dir, 'qtattributionsscanner')
    command = f'{scanner}  --output-format json {directory}'
    jsonS = subprocess.check_output(command, shell=True)
    if not jsonS:
        raise RuntimeError(f'{command} failed to produce output.')

    with open(targetFileName, 'w') as targetFile:
        targetFile.write(rstHeader)
        for entry in json.loads(jsonS.decode('utf-8')):
            content = f"{entry['Name']}\n{entry['Description']}\n{entry['QtUsage']}\n\n"
            url = entry['Homepage']
            version = entry['Version']
            if url and version:
                content = f"{content}{rstUrl('Project Homepage', url)}, upstream version: {version}\n\n"
            copyright = entry['Copyright']
            if copyright:
                content += rstLiteralBlockFromText(copyright)
            content += entry['License'] + '\n\n'
            licenseFile = entry['LicenseFile']
            if licenseFile:
                if Path(licenseFile).is_file():
                    content += rstLiteralBlock(readFile(licenseFile))
                else:
                    warnings.warn(f'"{licenseFile}" is not a file', RuntimeWarning)
            targetFile.write(content)


if __name__ == '__main__':
    parser = ArgumentParser(description=USAGE, formatter_class=RawTextHelpFormatter)
    parser.add_argument("-l", "--libexec", type=str, help="libexec directory of Qt")
    parser.add_argument('directory')
    parser.add_argument('target')
    options = parser.parse_args()
    directory = options.directory
    targetFileName = options.target
    libexec_dir = options.libexec
    if not libexec_dir:
        libexec_dir = get_libexec_dir()
    runScanner(directory, targetFileName, libexec_dir)
