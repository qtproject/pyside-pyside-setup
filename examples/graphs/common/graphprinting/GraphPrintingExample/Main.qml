// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtCore
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Fusion
import QtQuick.Dialogs

Rectangle {
    id: mainView
    width: 1280
    height: 720
    color: Application.styleHints.colorScheme === Qt.Dark ? "darkgray" : "lightgray"

    property var item: stackLayout.itemAt(stackLayout.currentIndex)
    property var outputsize: Qt.size(linegraph.width * 4, linegraph.height * 4)

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.rightMargin: 5
        anchors.topMargin: 5
        anchors.bottomMargin: 5
        spacing: 5

        GroupBox {
            id: groupBox
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            title: qsTr("Printing and exporting")

            ColumnLayout {
                id: buttonLayout
                spacing: 0
                uniformCellSizes: true
                Button {
                    id: captureButton
                    text: qsTr("Save to PDF")
                    flat: true

                    icon.source: pressed ? "documents_fill.svg" : "documents.svg"
                    icon.height: 36
                    icon.width: 36

                    onPressed: dialog.open()
                }

                Button {
                    id: printButton
                    text: qsTr("Send to printer")
                    flat: true

                    icon.source: pressed ? "print_fill.svg" : "print.svg"
                    icon.height: 36
                    icon.width: 36

                    onPressed: printerDialog.open()
                }
            }
        }

        Item {
            id: tabGroup
            Layout.fillHeight: true
            Layout.fillWidth: true

            TabBar {
                id: tabBar
                anchors.left: parent.left
                anchors.right: parent.right

                TabButton {
                    text: "2D Graph"
                    implicitHeight: 48
                    icon.source: checked ? "flatten_square_fill.svg" : "flatten.svg"
                    icon.height: 36
                    icon.width: 36
                }

                TabButton {
                    text: "3D Graph"
                    implicitHeight: 48
                    icon.source: checked ? "box_left_fill.svg" : "box_left.svg"
                    icon.height: 36
                    icon.width: 36
                }
            }
            Frame {
                id: tabFrame
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: tabBar.bottom
                anchors.bottom: parent.bottom

                StackLayout {
                    id: stackLayout

                    anchors.fill: parent
                    currentIndex: tabBar.currentIndex

                    Graph2D {
                        id: linegraph
                    }

                    Graph3D {
                        id: bargraph
                    }
                }
            }
        }
    }

    MessageDialog {
        id: message
        onButtonClicked: mainView.cleanAfterPrint()
    }

    FileDialog {
        id: dialog
        currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
        nameFilters: ["PDF files (*.pdf)"]
        defaultSuffix: "pdf"

        fileMode: FileDialog.SaveFile
        onAccepted: {
            mainView.prepareForPrint()

            mainView.item.grabToImage(function (result) {
                message.title = "Save PDF"
                message.text = "PDF saved to " + graphPrinter.generatePDF(
                            dialog.selectedFile, result.image)
                message.open()
            }, mainView.outputsize)
        }
    }

    Dialog {
        id: printerDialog
        anchors.centerIn: parent
        contentHeight: printerListView.height
        contentWidth: printerListView.width

        title: qsTr("Available Printers")
        modal: true

        onOpened: {
            printerModel.clear()
            var printers = graphPrinter.getPrinters()
            printers.forEach((x, i) => printerModel.append({
                                                               "name": x
                                                           }))
        }

        onAccepted: {
            var selectedPrinter = printerModel.get(printerListView.currentIndex)
            mainView.prepareForPrint()
            mainView.item.grabToImage(function (result) {
                message.title = "Print"
                message.text = graphPrinter.print(result.image,
                                                  selectedPrinter.name)
                message.open()
            }, mainView.outputsize)
        }

        onClosed: {
            mainView.cleanAfterPrint()
        }

        Component {
            id: printerDelegate
            Rectangle {
                width: 198
                height: 25
                color: "transparent"
                border.color: mainView.item.theme.grid.mainColor
                clip: true

                Text {
                    padding: 5
                    text: qsTr("<b>%1</b>").arg(name)
                    color: mainView.item.theme.labelTextColor
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: printerListView.currentIndex = index
                }
            }
        }

        contentItem: Rectangle {
            id: printerItem
            height: printerListView.height
            width: printerListView.width
            color: mainView.item.theme.plotAreaBackgroundColor

            ListView {
                id: printerListView
                height: 100
                width: 200
                clip: true

                model: printerModel
                delegate: printerDelegate
                highlight: Rectangle {
                    color: mainView.item.theme.grid.subColor
                }
            }
        }

        footer: DialogButtonBox {
            Button {
                text: "Print"
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
            }
            Button {
                text: "Cancel"
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
            }
        }
    }

    ListModel {
        id: printerModel
    }

    function prepareForPrint() {
        if (stackLayout.currentIndex === 1) {
            var newsize = Qt.size(bargraph.width * 4, bargraph.height * 4)

            // check that we do not exceed maximum texture size
            if (newsize.width * Screen.devicePixelRatio > graphPrinter.maxTextureSize ) {
                // scale to 25% under max texture size to be on the safe side; some GPUs seem
                // to glitch when using the abosulute max
                var ratio = (newsize.width * Screen.devicePixelRatio * 1.25)
                        / graphPrinter.maxTextureSize
                newsize.width /= ratio
                newsize.height /= ratio
            }
            outputsize.width = Math.round(newsize.width)
            outputsize.height = Math.round(newsize.height)

            // resize the bar graph to match the PDF output size
            item.width = outputsize.width
            item.height = outputsize.height
        } else {
            outputsize = Qt.size(linegraph.width * 4, linegraph.height * 4)
        }
    }

    function cleanAfterPrint() {
        if (stackLayout.currentIndex === 1) {
            // resize the bar graph back to the actual visual size
            item.width = stackLayout.width
            item.height = stackLayout.height
        }
    }
}
