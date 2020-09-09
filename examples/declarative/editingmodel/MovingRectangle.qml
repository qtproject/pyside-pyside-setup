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
