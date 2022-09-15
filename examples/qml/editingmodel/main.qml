// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Window
import BaseModel

Window {
    title: "Moving Rectangle"
    width: 800
    height: 480
    visible: true
    id: mainWindow

    Column {
        spacing: 20
        anchors.fill: parent
        id: mainColumn
        Text {
            padding: 20
            font.pointSize: 10
            width: 600
            wrapMode: Text.Wrap
            text: "This example shows how to add, remove and move items inside a QML ListView.\n
It shows and edits data via roles using QAbstractListModel on the Python side.\n
Use the 'Middle click' on top of a rectangle to remove an item.\n
'Left click' and drag to move the items."
        }

        Button {
            anchors {
                left: mainColumn.left
                right: mainColumn.right
                margins: 30
            }
            text: "Reset view"
            onClicked: lv.model.reset()
        }

        Button {
            anchors {
                left: mainColumn.left
                right: mainColumn.right
                margins: 30
            }
            text: "Add element"
            onClicked: lv.model.append()
        }

        ListView {
            id: lv
            anchors {
                left: mainColumn.left
                right: mainColumn.right
                margins: 30
            }

            height: 200
            model: BaseModel {}
            orientation: ListView.Horizontal
            displaced: Transition {
                NumberAnimation {
                    properties: "x,y"
                    easing.type: Easing.OutQuad
                }
            }
            delegate: DropArea {
                id: droparea
                width: ratio * lv.width
                height: lv.height

                onEntered: function (drag) {
                    let dragindex = drag.source.modelIndex
                    if (index === dragindex)
                        return
                    lv.model.move(dragindex, index)
                }

                MovingRectangle {
                    modelIndex: index
                    dragParent: lv
                    sizeParent: droparea
                }
            }

            MouseArea {
                id: lvMousearea
                anchors.fill: lv
                z: -1
            }
            Rectangle {
                id: lvBackground
                anchors.fill: lv
                anchors.margins: -border.width
                color: "white"
                border.color: "black"
                border.width: 5
                z: -1
            }
            Component.onCompleted: {
                lv.model.reset()
            }
        }
    }
}
