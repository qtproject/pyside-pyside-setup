# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import os
from random import randint


def adjust_filename(filename, orig_mod_filename):
    dirpath = os.path.dirname(os.path.abspath(orig_mod_filename))
    return os.path.join(dirpath, filename)


def _join_qml_errors(errors):
    '''Return an error string from a list of QQmlError'''
    result = ''
    for i, error in enumerate(errors):
        if i:
            result += ', '
        result += error.toString()
    return result


def quickview_errorstring(quickview):
    '''Return an error string from a QQuickView'''
    return _join_qml_errors(quickview.errors())


def qmlcomponent_errorstring(component):
    '''Return an error string from a QQmlComponent'''
    return _join_qml_errors(component.errors())


def random_string(size=5):
    '''Generate random string with the given size'''
    return ''.join(map(chr, [randint(33, 126) for x in range(size)]))
