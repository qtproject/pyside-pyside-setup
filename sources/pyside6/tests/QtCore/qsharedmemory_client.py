# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
