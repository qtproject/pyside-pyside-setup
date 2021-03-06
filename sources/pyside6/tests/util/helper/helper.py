#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
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
