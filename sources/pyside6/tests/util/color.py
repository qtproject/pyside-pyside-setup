# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Function to print a colored line to terminal'''


def print_colored(message):
    print(f'\033[0;31m{message}\033[m')  # red


if __name__ == '__main__':
    print('42 - the answer')
    print_colored("But what's the question?")
    print('Hum?')
