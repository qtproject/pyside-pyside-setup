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

'''Client for the unit test of QSharedMemory'''

import sys

from PySide6.QtCore import QSharedMemory


def read_string(shared_memory):
    """Read out a null-terminated string from the QSharedMemory"""
    mv = memoryview(shared_memory.constData())
    result = ''
    for i in range(shared_memory.size()):
        char = mv[i]
        if not char:
            break
        result += chr(char)
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Pass segment name', file=sys.stderr)
        sys.exit(-1)
    shared_memory = QSharedMemory(sys.argv[1])
    if not shared_memory.attach(QSharedMemory.ReadOnly):
        raise SystemError(f'attach to "{name}" failed')
    if not shared_memory.lock():
        raise SystemError(f'lock of "{name}" failed')
    data = read_string(shared_memory)
    shared_memory.unlock()
    shared_memory.detach()
    sys.stdout.write(data)
    sys.exit(0)
