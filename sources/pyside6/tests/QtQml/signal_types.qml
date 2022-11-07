// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick
import test.Obj

Rectangle {
    visible: true
    required property Obj o

    Connections {
        target: o
        function onListSignal(list) {
            var json_data = JSON.stringify(list)
            console.log("Connections.onListSignal: " + typeof(list) + " " + json_data)
            o.list_slot(list)
            o.json_slot(json_data)
        }
        function onDictSignal(dict) {
            var json_data = JSON.stringify(dict)
            console.log("Connections.onDictSignal: " + typeof(dict) + " " + json_data)
            o.dict_slot(dict)
            o.json_slot(json_data)
        }
    }
}
