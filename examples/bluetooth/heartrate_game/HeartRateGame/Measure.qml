// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import HeartRateGame

GamePage {
    id: measurePage

    required property DeviceHandler deviceHandler

    errorMessage: deviceHandler.error
    infoMessage: deviceHandler.info
    iconType: deviceHandler.icon

    property real __timeCounter: 0
    property real __maxTimeCount: 60

    readonly property string relaxText: qsTr("Relax!")
    readonly property string startText: qsTr("When you are ready,\npress Start.")
    readonly property string instructionText: qsTr("You have %1s time to increase heart\nrate as much as possible.").arg(__maxTimeCount)
    readonly property string goodLuckText: qsTr("Good luck!")

    signal showStatsPage

    function close() {
        deviceHandler.stopMeasurement()
        deviceHandler.disconnectService()
    }

    function start() {
        if (!deviceHandler.measuring) {
            __timeCounter = 0
            deviceHandler.startMeasurement()
        }
    }

    function stop() {
        if (deviceHandler.measuring)
            deviceHandler.stopMeasurement()

        measurePage.showStatsPage()
    }

    Timer {
        id: measureTimer
        interval: 1000
        running: measurePage.deviceHandler.measuring
        repeat: true
        onTriggered: {
            measurePage.__timeCounter++
            if (measurePage.__timeCounter >= measurePage.__maxTimeCount)
                measurePage.stop()
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: GameSettings.fieldHeight * 0.5

        Rectangle {
            id: circle

            readonly property bool hintVisible: !measurePage.deviceHandler.measuring
            readonly property real innerSpacing: Math.min(width * 0.05, 25)

            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.min(measurePage.width, measurePage.height - GameSettings.fieldHeight * 4)
                   - 2 * GameSettings.fieldMargin
            height: width
            radius: width * 0.5
            color: GameSettings.viewColor

            Text {
                id: relaxTextBox
                anchors {
                    bottom: startTextBox.top
                    bottomMargin: parent.innerSpacing
                    horizontalCenter: parent.horizontalCenter
                }
                width: parent.width * 0.6
                height: parent.height * 0.1
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: measurePage.relaxText
                visible: circle.hintVisible
                color: GameSettings.textColor
                fontSizeMode: Text.Fit
                font.pixelSize: GameSettings.smallFontSize
                font.bold: true
            }

            Text {
                id: startTextBox
                anchors {
                    bottom: heart.top
                    bottomMargin: parent.innerSpacing
                    horizontalCenter: parent.horizontalCenter
                }
                width: parent.width * 0.8
                height: parent.height * 0.15
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: measurePage.startText
                visible: circle.hintVisible
                color: GameSettings.textColor
                fontSizeMode: Text.Fit
                font.pixelSize: GameSettings.tinyFontSize
            }

            Text {
                id: measureTextBox
                anchors {
                    bottom: heart.top
                    horizontalCenter: parent.horizontalCenter
                }
                width: parent.width * 0.7
                height: parent.height * 0.35
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: measurePage.deviceHandler.hr
                visible: measurePage.deviceHandler.measuring
                color: GameSettings.heartRateColor
                fontSizeMode: Text.Fit
                font.pixelSize: GameSettings.hugeFontSize
                font.bold: true
            }

            Image {
                id: heart
                anchors.centerIn: circle
                width: parent.width * 0.2
                height: width
                fillMode: Image.PreserveAspectFit
                source: "images/heart.png"
                smooth: true
                antialiasing: true

                SequentialAnimation {
                    id: heartAnim
                    running: measurePage.deviceHandler.measuring
                    loops: Animation.Infinite
                    alwaysRunToEnd: true
                    PropertyAnimation {
                        target: heart
                        property: "scale"
                        to: 1.4
                        duration: 500
                        easing.type: Easing.InQuad
                    }
                    PropertyAnimation {
                        target: heart
                        property: "scale"
                        to: 1.0
                        duration: 500
                        easing.type: Easing.OutQuad
                    }
                }
            }

            Text {
                id: instructionTextBox
                anchors {
                    top: heart.bottom
                    topMargin: parent.innerSpacing
                    horizontalCenter: parent.horizontalCenter
                }
                width: parent.width * 0.8
                height: parent.height * 0.15
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: measurePage.instructionText
                visible: circle.hintVisible
                color: GameSettings.textColor
                fontSizeMode: Text.Fit
                font.pixelSize: GameSettings.tinyFontSize
            }

            Text {
                id: goodLuckBox
                anchors {
                    top: instructionTextBox.bottom
                    topMargin: parent.innerSpacing
                    horizontalCenter: parent.horizontalCenter
                }
                width: parent.width * 0.6
                height: parent.height * 0.1
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: measurePage.goodLuckText
                visible: circle.hintVisible
                color: GameSettings.textColor
                fontSizeMode: Text.Fit
                font.pixelSize: GameSettings.smallFontSize
                font.bold: true
            }

            Item {
                id: minMaxContainer
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width * 0.7
                height: parent.height * 0.15
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height * 0.16
                visible: measurePage.deviceHandler.measuring

                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width * 0.35
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    text: measurePage.deviceHandler.minHR
                    color: GameSettings.textColor
                    fontSizeMode: Text.Fit
                    font.pixelSize: GameSettings.largeFontSize

                    Text {
                        anchors.left: parent.left
                        anchors.bottom: parent.top
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        width: parent.width
                        fontSizeMode: Text.Fit
                        font.pixelSize: GameSettings.mediumFontSize
                        color: parent.color
                        text: "MIN"
                    }
                }

                Text {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    width: parent.width * 0.35
                    text: measurePage.deviceHandler.maxHR
                    color: GameSettings.textColor
                    fontSizeMode: Text.Fit
                    font.pixelSize: GameSettings.largeFontSize

                    Text {
                        anchors.right: parent.right
                        anchors.bottom: parent.top
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        width: parent.width
                        fontSizeMode: Text.Fit
                        font.pixelSize: GameSettings.mediumFontSize
                        color: parent.color
                        text: "MAX"
                    }
                }
            }
        }

        Rectangle {
            id: timeSlider
            color: GameSettings.viewColor
            anchors.horizontalCenter: parent.horizontalCenter
            width: circle.width
            height: GameSettings.fieldHeight
            radius: GameSettings.buttonRadius
            border {
                width: 1
                color: GameSettings.sliderBorderColor
            }

            Rectangle {
                anchors {
                    top: parent.top
                    topMargin: parent.border.width
                    left: parent.left
                    leftMargin: parent.border.width
                }
                height: parent.height - 2 * parent.border.width
                width: Math.min(1.0, measurePage.__timeCounter / measurePage.__maxTimeCount)
                       * (parent.width - 2 * parent.border.width)
                radius: parent.radius
                color: GameSettings.sliderColor
            }

            Image {
                readonly property int imgSize: GameSettings.fieldHeight * 0.5
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: GameSettings.fieldMargin * 0.5
                }
                source: "images/clock.svg"
                sourceSize.width: imgSize
                sourceSize.height: imgSize
                fillMode: Image.PreserveAspectFit
            }

            Text {
                anchors.centerIn: parent
                color: GameSettings.sliderTextColor
                text: (measurePage.__maxTimeCount - measurePage.__timeCounter).toFixed(0) + " s"
                font.pixelSize: GameSettings.smallFontSize
            }
        }
    }

    GameButton {
        id: startButton
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: GameSettings.fieldMargin
        width: circle.width
        height: GameSettings.fieldHeight
        enabled: measurePage.deviceHandler.alive && !measurePage.deviceHandler.measuring
                 && measurePage.errorMessage === ""
        radius: GameSettings.buttonRadius

        onClicked: measurePage.start()

        Text {
            anchors.centerIn: parent
            font.pixelSize: GameSettings.microFontSize
            text: qsTr("START")
            color: GameSettings.textDarkColor
        }
    }
}
