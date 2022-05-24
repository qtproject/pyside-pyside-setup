// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

Rectangle {
    width: 500
    height: 500
    color: 'red'

    property variant pythonObject: undefined

    Text {
        anchors.centerIn: parent
        text: 'click me'
        color: 'white'
    }

    onPythonObjectChanged: {
        if (pythonObject) {
            // Delay execution of method invocation, so that the event loop has a chance to start,
            // which will subsequently be stopped by the method.
            timer.start()
        }
    }

    Timer {
        id: timer
        interval: 100; running: false;
        onTriggered: {
            if (pythonObject) {
                pythonObject.blubb(42, 84)
            }
        }
    }
}

