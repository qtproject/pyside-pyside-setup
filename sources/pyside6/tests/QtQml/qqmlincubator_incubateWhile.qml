// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
import QtQuick 2.0


Rectangle {
    id: root
    objectName: "theNicestRoot"
    width: 400; height: 400

    signal shouldInterrupt()
    property int loadedItems: 0
    property int itemsToCreate: 10

    Row {
        anchors.centerIn: parent
        spacing: 20

        Rectangle {
            id: initialRectangle
            width: 10; height: 10
            color: "red"
        }

        Repeater {
            model: itemsToCreate
            Loader {
                id: loader
                asynchronous: true
                source: "qqmlincubator_incubateWhile_component.qml"
                onLoaded: {
                    root.loadedItems += 1

                    // Interrupt incubation after half of the items are loaded.
                    if (root.loadedItems >= (itemsToCreate / 2)) {
                        root.shouldInterrupt()
                    }
                }
            }
        }
    }
}
