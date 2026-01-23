// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    property int modelIndex
    property Item dragParent
    property Item sizeParent
    property alias text: zone.text
    property alias bgColor: root.color

    anchors {
        horizontalCenter: parent.horizontalCenter
        verticalCenter: parent.verticalCenter
    }
    color:  backgroundColor
    anchors.fill: sizeParent
    border.color: "yellow"
    border.width: 0
    TextArea {
        id: zone
        anchors.centerIn: parent
        text: display
        onTextChanged: model.edit = text
    }

    MouseArea {
        id: zoneMouseArea
        anchors.fill: parent

        acceptedButtons: Qt.MiddleButton
        onClicked: function(mouse) {
            if (mouse.button == Qt.MiddleButton)
                lv.model.remove(index)
            else
                mouse.accepted = false
        }
    }
    DragHandler {
        id: dragHandler
        xAxis {

            enabled: true
            minimum: 0
            maximum: lv.width - droparea.width
        }
        yAxis.enabled: false
        acceptedButtons: Qt.LeftButton
    }
    Drag.active: dragHandler.active
    Drag.source: root
    Drag.hotSpot.x: width / 2

    states: [
        State {
            when: dragHandler.active
            ParentChange {
                target: root
                parent: root.dragParent
            }

            AnchorChanges {
                target: root
                anchors.horizontalCenter: undefined
                anchors.verticalCenter: undefined
            }
            PropertyChanges {
                target: root
                opacity: 0.6
                border.width: 3
            }
        }
    ]
}
