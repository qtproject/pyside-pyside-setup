// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ChatModel

ApplicationWindow {
    id: window
    title: qsTr("Chat")
    width: 640
    height: 960
    visible: true

    SqlConversationModel {
        id: chat_model
    }

    ColumnLayout {
        anchors.fill: parent

        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: pane.leftPadding + messageField.leftPadding
            displayMarginBeginning: 40
            displayMarginEnd: 40
            verticalLayoutDirection: ListView.BottomToTop
            spacing: 12
            model: chat_model
            delegate: Column {
                anchors.right: sentByMe ? listView.contentItem.right : undefined
                spacing: 6

                readonly property bool sentByMe: model.recipient !== "Me"
                Row {
                    id: messageRow
                    spacing: 6
                    anchors.right: sentByMe ? parent.right : undefined

                    Rectangle {
                        width: Math.min(messageText.implicitWidth + 24,
                            listView.width - (!sentByMe ? messageRow.spacing : 0))
                        height: messageText.implicitHeight + 24
                        radius: 15
                        color: sentByMe ? "lightgrey" : "steelblue"

                        Label {
                            id: messageText
                            text: model.message
                            color: sentByMe ? "black" : "white"
                            anchors.fill: parent
                            anchors.margins: 12
                            wrapMode: Label.Wrap
                        }
                    }
                }

                Label {
                    id: timestampText
                    text: Qt.formatDateTime(model.timestamp, "d MMM hh:mm")
                    color: "lightgrey"
                    anchors.right: sentByMe ? parent.right : undefined
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }

        Pane {
            id: pane
            Layout.fillWidth: true

            RowLayout {
                width: parent.width

                TextArea {
                    id: messageField
                    Layout.fillWidth: true
                    placeholderText: qsTr("Compose message")
                    wrapMode: TextArea.Wrap
                }

                Button {
                    id: sendButton
                    text: qsTr("Send")
                    enabled: messageField.length > 0
                    onClicked: {
                        listView.model.send_message("machine", messageField.text, "Me");
                        messageField.text = "";
                    }
                }
            }
        }
    }
}
