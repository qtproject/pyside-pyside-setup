/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: http://www.qt.io/licensing/
**
** This file is part of the Qt for Python examples of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:BSD$
** You may use this file under the terms of the BSD license as follows:
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Neither the name of The Qt Company Ltd nor the names of its
**     contributors may be used to endorse or promote products derived
**     from this software without specific prior written permission.
**
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
** LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
** A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
** OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
** SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
** LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
** DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
** THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
