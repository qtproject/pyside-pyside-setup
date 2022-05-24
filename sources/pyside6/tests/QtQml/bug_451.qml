// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0
import test.PythonObject 1.0

Rectangle {
    id: page
    required property PythonObject python

    function simpleFunction() {
        python.called = "simpleFunction"
    }

    function oneArgFunction(x) {
        python.called = "oneArgFunction"
        python.arg1 = x
    }

    function twoArgFunction(x, y) {
        python.called = "twoArgFunction"
        python.arg1 = x
        python.arg2 = y
    }

    function returnFunction() {
        python.called = "returnFunction"
        return 42
    }

}
