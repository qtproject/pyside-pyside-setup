#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# This is a small script printing out Qt binding class hierarchies
# for comparison purposes.
#
# Usage:
#
# ./list-class-hierarchy.py PySide6 > pyside6.list
# ./list-class-hierarchy.py PyQt5 > pyqt5.list
#
# meld pyside.list pyqt5.list

import sys
import pdb
from inspect import isclass

ignore = ["staticMetaObject",
          "pyqtConfigure",
          "registerUserData",
          "thread",
         ]


def recurse_into(el, obj):
    #s = el.split('.')[-1]
    #pdb.set_trace()
    symbols = []
    for item in sorted(dir(obj)):
        if item[0] == '_':
            continue
        mel = el + '.' + item
        try:
            mobj = eval(mel)
        except Exception:
            continue

        if item in ignore:
            continue
        else:
            symbols.append(mel)

        if isclass(mobj):
            symbols += recurse_into(mel, mobj)

    return symbols


if __name__=='__main__':
    modules = [ 'QtCore',
                'QtGui',
                'QtHelp',
               #'QtMultimedia',
                'QtNetwork',
               #'QtOpenGL',
                'QtScript',
                'QtScriptTools',
                'QtSql',
                'QtSvg',
                'QtTest',
               #'QtUiTools',
                'QtXml',
                'QtXmlPatterns' ]

    libraries = ["PySide6", "PyQt5"]
    librarySymbols = {}
    for l in libraries:
        dictionary = []
        if l == "PyQt5":
            import sip
            sip.setapi('QDate', 2)
            sip.setapi('QDateTime', 2)
            sip.setapi('QString', 2)
            sip.setapi('QTextStream', 2)
            sip.setapi('QTime', 2)
            sip.setapi('QUrl', 2)
            sip.setapi('QVariant', 2)

        for m in modules:
            exec(f"from {l} import {m}", globals(), locals())
            dictionary += recurse_into(m, eval(m))
        librarySymbols[l] = dictionary

    print("PyQt5: ", len(librarySymbols["PyQt5"]), " PySide6: ", len(librarySymbols["PySide6"]))

    for symbol in librarySymbols["PyQt5"]:
        if not (symbol in librarySymbols["PySide6"]):
            print("Symbol not found in PySide6:", symbol)
