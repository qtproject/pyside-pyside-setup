// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

import QtExampleStyle

Popup {
    id: userMenu

    required property BasicLogin userLoginService
    required property PaginatedResource userMenuUsers

    width: 280
    height: 270

    background: Item {}

    Rectangle {
        radius: 8
        border.width: 0
        color: UIStyle.background

        anchors.fill: parent

        ListView {
            id: userListView
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 5
            anchors.topMargin: 5
            anchors.bottomMargin: 2

            model: userMenu.userMenuUsers.data
            spacing: 7
            footerPositioning: ListView.PullBackFooter
            clip: true

            Layout.fillHeight: true
            Layout.fillWidth: true

            delegate: Item {
                id: userInfo

                height: 30
                width: userListView.width

                required property var modelData
                readonly property bool logged: (modelData.email === userMenu.userLoginService.user)

                Item {
                    id: userImageCliped
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: 30
                    height: 30

                    Image {
                        id: userImage
                        anchors.fill: parent
                        source: userInfo.modelData.avatar
                        visible: false
                    }

                    Image {
                        id: userMask
                        source: "qrc:/qt/qml/ColorPalette/icons/userMask.svg"
                        anchors.fill: userImage
                        anchors.margins: 4
                        visible: false
                    }

                    MultiEffect {
                        source: userImage
                        anchors.fill: userImage
                        maskSource: userMask
                        maskEnabled: true
                    }
                }

                Text {
                    id: userMailLabel
                    anchors.left: userImageCliped.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 5
                    text: userInfo.modelData.email
                    color: UIStyle.textColor
                    font.bold: userInfo.logged
                }

                ToolButton {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 5

                    icon.source: UIStyle.iconPath(userInfo.logged
                                 ? "logout" : "login")
                    enabled: userInfo.logged || !userMenu.userLoginService.loggedIn

                    onClicked: {
                        if (userInfo.logged) {
                            userMenu.userLoginService.logout()
                        } else {
                            //! [Login]
                            userMenu.userLoginService.login({"email" : userInfo.modelData.email,
                                                "password" : "apassword",
                                                "id" : userInfo.modelData.id})
                            //! [Login]
                            userMenu.close()
                        }
                    }
                }

            }
            footer: ToolBar {
                // Paginate buttons if more than one page
                visible: userMenu.userMenuUsers.pages > 1
                implicitWidth: parent.width

                RowLayout {
                    anchors.fill: parent

                    Item { Layout.fillWidth: true /* spacer */ }

                    Repeater {
                        model: userMenu.userMenuUsers.pages

                        ToolButton {
                            text: page
                            font.bold: userMenu.userMenuUsers.page === page

                            required property int index
                            readonly property int page: (index + 1)

                            onClicked: userMenu.userMenuUsers.page = page
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        radius: 8
        border.color: UIStyle.buttonOutline
        border.width: 2
        color: "transparent"

        anchors.fill: parent
    }
}
