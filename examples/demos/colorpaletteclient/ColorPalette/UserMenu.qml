// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

import QtExampleStyle
import ColorPalette

Popup {
    id: userMenu

    required property BasicLogin userLoginService
    required property PaginatedColorUsersResource userMenuUsers

    width: 280
    height: 270

    ColumnLayout {
        anchors.fill: parent

        ListView {
            id: userListView

            model: userMenu.userMenuUsers.model
            spacing: 5
            footerPositioning: ListView.PullBackFooter
            clip: true

            Layout.fillHeight: true
            Layout.fillWidth: true

            delegate: Rectangle {
                id: userInfo

                required property string email
                required property string avatar

                height: 30
                width: userListView.width


                readonly property bool logged: (email === loginService.user)

                Rectangle {
                    id: userImageCliped
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: 30
                    height: 30

                    Image {
                        id: userImage
                        anchors.fill: parent
                        source: userInfo.avatar
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
                    text: userInfo.email
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
                            userMenu.userLoginService.login({"email" : userInfo.email,
                                                "password" : "apassword",
                                                "id" : userInfo.id})
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
}
