// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Shapes

import QtExampleStyle
import ColorPalette

Item {
    id: root
    required property BasicLogin loginService
    required property PaginatedColorsResource colors
    required property PaginatedColorUsersResource colorViewUsers

    ColorDialogEditor {
        id: colorPopup
        onColorAdded: (colorNameField, colorRGBField, colorPantoneField) => {
            root.colors.add({"name" : colorNameField,
                        "color" : colorRGBField,
                        "pantone_value" : colorPantoneField})
        }

        onColorUpdated: (colorNameField, colorRGBField, colorPantoneField, cid) => {
            root.colors.update({"name" : colorNameField,
                        "color" : colorRGBField,
                        "pantone_value" : colorPantoneField},
                        cid)
        }
    }

    ColorDialogDelete {
        id: colorDeletePopup
        onDeleteClicked: (cid) => {
            root.colors.remove(cid)
        }
    }

    ColumnLayout {
        // The main application layout
        anchors.fill :parent

        ToolBar {
            Layout.fillWidth: true
            Layout.minimumHeight: 25 + 4

            UserMenu {
                id: userMenu

                userMenuUsers: root.colorViewUsers
                userLoginService: root.loginService
            }

            RowLayout {
                anchors.fill: parent
                Text {
                    text: qsTr("QHTTP Server")
                    font.pixelSize: 8
                    color: "#667085"
                }
                Item { Layout.fillWidth: true }

                AbstractButton {
                    id: loginButton
                    Layout.preferredWidth: 25
                    Layout.preferredHeight: 25
                    Item {
                        id: userImageCliped
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: 25
                        height: 25

                        Image {
                            id: userImage
                            anchors.fill: parent
                            source: getCurrentUserImage()
                            visible: false

                            function getCurrentUserImage() {
                                if (root.loginService.loggedIn)
                                    return users.avatarForEmail(loginService.user)
                                return "qrc:/qt/qml/ColorPalette/icons/user.svg";
                            }
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

                    onClicked: {
                        userMenu.open()
                        var pos = mapToGlobal(Qt.point(x, y))
                        pos = userMenu.parent.mapFromGlobal(pos)
                        userMenu.x = x - userMenu.width + 25 + 3
                        userMenu.y = y + 25 + 3
                    }

                    Shape {
                       id: bubble
                       x: -text.width - 25
                       anchors.margins: 3

                       preferredRendererType: Shape.CurveRenderer

                        visible: !root.loginService.loggedIn

                       ShapePath {
                           strokeWidth: 0
                           fillColor: "#667085"
                           startX: 5; startY: 0
                           PathLine { x: 5 + text.width + 6; y: 0 }
                           PathArc { x: 10 + text.width + 6; y: 5; radiusX: 5; radiusY: 5}
                           // arrow
                           PathLine { x: 10 + text.width + 6; y: 8 + text.height / 2 - 6 }
                           PathLine { x: 10 + text.width + 6 + 6; y: 8 + text.height / 2 }
                           PathLine { x: 10 + text.width + 6; y: 8 + text.height / 2 + 6}
                           PathLine { x: 10 + text.width + 6; y: 5 + text.height + 6 }
                           // end arrow
                           PathArc { x: 5 + text.width + 6; y: 10 + text.height + 6 ; radiusX: 5; radiusY: 5}
                           PathLine { x: 5; y: 10 + text.height + 6 }
                           PathArc { x: 0; y: 5 + text.height + 6 ; radiusX: 5; radiusY: 5}
                           PathLine { x: 0; y: 5 }
                           PathArc { x: 5; y: 0 ; radiusX: 5; radiusY: 5}
                       }
                       Text {
                           x: 8
                           y: 8
                           id: text
                           color: "white"
                           text: qsTr("Log in to edit")
                           font.bold: true
                           horizontalAlignment: Qt.AlignHCenter
                           verticalAlignment: Qt.AlignVCenter
                       }
                   }
                }
            }

            Image {
                anchors.centerIn: parent
                source: "qrc:/qt/qml/ColorPalette/icons/qt.png"
                fillMode: Image.PreserveAspectFit
                height: 25
            }

        }
        ToolBar {
            Layout.fillWidth: true
            Layout.minimumHeight: 32

            RowLayout {
                anchors.fill: parent
                Text {
                    Layout.alignment: Qt.AlignVCenter
                    text: qsTr("Color Palette")
                    font.pixelSize: 14
                    font.bold: true
                    color: "#667085"
                }

                Item { Layout.fillWidth: true }

                AbstractButton {
                    Layout.preferredWidth: 25
                    Layout.preferredHeight: 25
                    Layout.alignment: Qt.AlignVCenter

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: "#192CDE85"
                        border.color: "#DDE2E8"
                        border.width: 1
                    }

                    Image {
                        source: UIStyle.iconPath("plus")
                        fillMode: Image.PreserveAspectFit
                        anchors.fill: parent
                        sourceSize.width: width
                        sourceSize.height: height

                    }
                    visible: root.loginService.loggedIn
                    onClicked: colorPopup.createNewColor()
                }

                AbstractButton {
                    Layout.preferredWidth: 25
                    Layout.preferredHeight: 25
                    Layout.alignment: Qt.AlignVCenter

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: "#192CDE85"
                        border.color: "#DDE2E8"
                        border.width: 1
                    }

                    Image {
                        source: UIStyle.iconPath("update")
                        fillMode: Image.PreserveAspectFit
                        anchors.fill: parent
                        sourceSize.width: width
                        sourceSize.height: height
                    }

                    onClicked: {
                        root.colors.refreshCurrentPage()
                        root.colorViewUsers.refreshCurrentPage()
                    }
                }
            }
        }



        //! [View and model]
        ListView {
            id: colorListView

            model: root.colors.model
        //! [View and model]
            footerPositioning: ListView.OverlayFooter
            spacing: 15
            clip: true

            Layout.fillHeight: true
            Layout.fillWidth: true

            header:  Rectangle {
                height: 32
                width: parent.width
                color: "#F0F1F3"

                RowLayout {
                    anchors.fill: parent

                    component HeaderText : Text {
                        Layout.alignment: Qt.AlignVCenter
                        horizontalAlignment: Qt.AlignHCenter

                        font.pixelSize: 12
                        color: "#667085"
                    }
                    HeaderText {
                        id: headerName
                        text: qsTr("Color Name")
                        Layout.preferredWidth: colorListView.width * 0.3
                    }
                    HeaderText {
                        id: headerRgb
                        text: qsTr("Rgb Value")
                        Layout.preferredWidth: colorListView.width * 0.25
                    }
                    HeaderText {
                        id: headerPantone
                        text: qsTr("Pantone Value")
                        Layout.preferredWidth: colorListView.width * 0.25
                    }
                    HeaderText {
                        id: headerAction
                        text: qsTr("Action")
                        Layout.preferredWidth: colorListView.width * 0.2
                    }
                }
            }

            delegate: Item {
                id: colorInfo

                required property int color_id
                required property string name
                required property string color
                required property string pantone_value

                width: colorListView.width
                height: 25
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5

                    Rectangle {
                        id: colorSample
                        Layout.alignment: Qt.AlignVCenter
                        implicitWidth: 36
                        implicitHeight: 21
                        radius: 6
                        color: colorInfo.color
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.3 - colorSample.width
                        horizontalAlignment: Qt.AlignLeft
                        leftPadding: 5
                        text: colorInfo.name
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.25
                        horizontalAlignment: Qt.AlignHCenter
                        text: colorInfo.color
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.25
                        horizontalAlignment: Qt.AlignHCenter
                        text: colorInfo.pantone_value
                    }

                    Item {
                        Layout.maximumHeight: 28
                        implicitHeight: buttonBox.implicitHeight
                        implicitWidth: buttonBox.implicitWidth

                        RowLayout {
                            id: buttonBox
                            anchors.fill: parent
                            ToolButton {
                                icon.source: UIStyle.iconPath("delete")
                                enabled: root.loginService.loggedIn
                                onClicked: colorDeletePopup.maybeDelete(color_id, name)
                            }
                            ToolButton {
                                icon.source: UIStyle.iconPath("edit")
                                enabled: root.loginService.loggedIn
                                onClicked: colorPopup.updateColor(color_id, name, color, pantone_value)
                            }
                        }
                    }
                }
            }

            footer: ToolBar {
                // Paginate buttons if more than one page
                visible: root.colors.pages > 1
                implicitWidth: parent.width

                RowLayout {
                    anchors.fill: parent

                    Item { Layout.fillWidth: true /* spacer */ }

                    Repeater {
                        model: root.colors.pages

                        ToolButton {
                            text: page
                            font.bold: root.colors.page === page

                            required property int index
                            readonly property int page: (index + 1)

                            onClicked: root.colors.page = page
                        }
                    }
                }
            }
        }
    }
}
