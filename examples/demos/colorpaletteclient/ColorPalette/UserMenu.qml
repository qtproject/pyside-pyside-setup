// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

Popup {
    id: userMenu

    required property BasicLogin userLoginService
    required property PaginatedResource userMenuUsers

    width: 280
    height: 270

    background: Item {}

    function iconPath(baseImagePath) {
        return Application.styleHints.colorScheme === Qt.ColorScheme.Dark
            ? `qrc:/qt/qml/ColorPalette/icons/${baseImagePath}_dark.svg`
            : `qrc:/qt/qml/ColorPalette/icons/${baseImagePath}.svg`
    }

    Rectangle {
        radius: 8
        border.width: 0
        color: palette.window

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

                Label {
                    id: userMailLabel
                    anchors.left: userImageCliped.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 5
                    text: userInfo.modelData.email
                    font.bold: userInfo.logged
                }

                ToolButton {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 5

                    icon.source: userMenu.iconPath(userInfo.logged
                                 ? "logout" : "login")
                    enabled: userInfo.logged || !userMenu.userLoginService.loggedIn

                    ToolTip.visible: hovered
                    ToolTip.delay: 500
                    ToolTip.text: userInfo.logged
                                  ? qsTr("Log out")
                                  : qsTr("Log in as %1").arg(userInfo.modelData.email)

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

                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: qsTr("Go to page %1").arg(page)

                            onClicked: userMenu.userMenuUsers.page = page
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        radius: 8
        border.color: palette.mid
        border.width: 2
        color: "transparent"

        anchors.fill: parent
    }
}
