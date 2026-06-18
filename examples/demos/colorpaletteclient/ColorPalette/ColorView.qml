// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Shapes

import QtExampleStyle

Rectangle {
    id: root
    required property BasicLogin loginService
    required property PaginatedResource colors
    required property PaginatedResource colorViewUsers

    color: UIStyle.background

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
        spacing: 0
        ToolBar {
            Layout.fillWidth: true
            Layout.minimumHeight: 35

            UserMenu {
                id: userMenu

                userMenuUsers: root.colorViewUsers
                userLoginService: root.loginService
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 5
                anchors.rightMargin: 5

                AbstractButton {
                    Layout.preferredWidth: 25
                    Layout.preferredHeight: 25
                    Layout.alignment: Qt.AlignVCenter

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: UIStyle.buttonBackground
                        border.color: UIStyle.buttonOutline
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
                        color: UIStyle.buttonBackground
                        border.color: UIStyle.buttonOutline
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

                Item { Layout.fillWidth: true }

                Image {
                    Layout.preferredWidth: 25
                    Layout.preferredHeight: 25
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft

                    source: "qrc:/qt/qml/ColorPalette/icons/qt.png"
                    fillMode: Image.PreserveAspectFit
                }

                Text {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft

                    text: qsTr("Color Palette")
                    font.pixelSize: UIStyle.fontSizeM
                    font.bold: true
                    color: UIStyle.titletextColor
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
                                if (!root.loginService.loggedIn)
                                    return UIStyle.iconPath("user");
                                let users = root.colorViewUsers
                                for (let i = 0; i < users.data.length; i++) {
                                    if (users.data[i].email === root.loginService.user)
                                        return users.data[i].avatar;
                                }
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
                        userMenu.x = x - userMenu.width + 50
                        userMenu.y = y + 15
                    }

                    Shape {
                       id: bubble
                       x: -text.width - 25
                       y: -3
                       anchors.margins: 3

                       preferredRendererType: Shape.CurveRenderer

                        visible: !root.loginService.loggedIn

                       ShapePath {
                           strokeWidth: 0
                           fillColor: UIStyle.highlightColor
                           strokeColor: UIStyle.highlightBorderColor
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
                           color: UIStyle.textColor
                           text: qsTr("Log in to edit")
                           font.bold: true
                           horizontalAlignment: Qt.AlignHCenter
                           verticalAlignment: Qt.AlignVCenter
                       }
                   }
                }

            }
        }



        //! [View and model]
        ListView {
            id: colorListView

            model: root.colors.data
        //! [View and model]
            footerPositioning: ListView.OverlayFooter
            spacing: 15
            clip: true

            Layout.fillHeight: true
            Layout.fillWidth: true

            header:  Rectangle {
                height: 32
                width: parent.width
                color: UIStyle.background

                RowLayout {
                    anchors.fill: parent

                    component HeaderText : Text {
                        Layout.alignment: Qt.AlignVCenter
                        horizontalAlignment: Qt.AlignHCenter

                        font.pixelSize: UIStyle.fontSizeS
                        color: UIStyle.titletextColor
                    }
                    HeaderText {
                        id: headerName
                        text: qsTr("Color Name")
                        Layout.fillWidth: true
                        Layout.horizontalStretchFactor: 30
                    }
                    HeaderText {
                        id: headerRgb
                        text: qsTr("Rgb Value")
                        Layout.fillWidth: true
                        Layout.horizontalStretchFactor: 25
                    }
                    HeaderText {
                        id: headerPantone
                        text: qsTr("Pantone Value")
                        Layout.fillWidth: true
                        Layout.horizontalStretchFactor: 25
                        font.pixelSize: UIStyle.fontSizeS
                    }
                    HeaderText {
                        id: headerAction
                        text: qsTr("Action")
                        Layout.fillWidth: true
                        Layout.horizontalStretchFactor: 20
                    }
                }
            }

            delegate: Item {
                id: colorInfo

                required property var modelData

                width: colorListView.width
                height: (colorListView.height - 55) / 6 - colorListView.spacing
                // Header: 35, Footer 20, 55 together
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5

                    Rectangle {
                        id: colorSample
                        Layout.alignment: Qt.AlignVCenter
                        implicitWidth: 36
                        implicitHeight: 36
                        radius: 6
                        color: colorInfo.modelData.color
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.3 - colorSample.width
                        horizontalAlignment: Qt.AlignLeft
                        leftPadding: 5
                        text: colorInfo.modelData.name
                        color: UIStyle.textColor
                        font.pixelSize: UIStyle.fontSizeS
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.25
                        horizontalAlignment: Qt.AlignHCenter
                        text: colorInfo.modelData.color
                        color: UIStyle.textColor
                        font.pixelSize: UIStyle.fontSizeS
                    }

                    Text {
                        Layout.preferredWidth: colorInfo.width * 0.25
                        horizontalAlignment: Qt.AlignHCenter
                        text: colorInfo.modelData.pantone_value
                        color: UIStyle.textColor
                        font.pixelSize: UIStyle.fontSizeS
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
                                onClicked: colorDeletePopup.maybeDelete(colorInfo.modelData)
                            }
                            ToolButton {
                                icon.source: UIStyle.iconPath("edit")
                                enabled: root.loginService.loggedIn
                                onClicked: colorPopup.updateColor(colorInfo.modelData)
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
