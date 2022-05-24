// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0
import Example 1.0

Rectangle {
    width: 100
    height: 62

    MyClass {
        id: myClass
        urla: "http://www.pyside.org"
    }

    Text {
        id: name
        text: myClass.urla
    }
}
