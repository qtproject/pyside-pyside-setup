// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma Singleton
import QtQuick

QtObject {
    property int wHeight
    property int wWidth

    // Colors
    readonly property color lightGreenColor: "#80ebb6"
    readonly property color backgroundColor: "#2c3038"
    readonly property color buttonColor: "#2cde85"
    readonly property color buttonPressedColor: lightGreenColor
    readonly property color disabledButtonColor: "#808080"
    readonly property color viewColor: "#262626"
    readonly property color delegate1Color: "#262626"
    readonly property color delegate2Color: "#404040"
    readonly property color textColor: "#ffffff"
    readonly property color textDarkColor: "#0d0d0d"
    readonly property color textInfoColor: lightGreenColor
    readonly property color sliderColor: "#00414a"
    readonly property color sliderBorderColor: lightGreenColor
    readonly property color sliderTextColor: lightGreenColor
    readonly property color errorColor: "#ba3f62"
    readonly property color infoColor: lightGreenColor
    readonly property color titleColor: "#202227"
    readonly property color selectedTitleColor: "#19545c"
    readonly property color hoverTitleColor: Qt.rgba(selectedTitleColor.r,
                                                     selectedTitleColor.g,
                                                     selectedTitleColor.b,
                                                     0.25)
    readonly property color bottomLineColor: "#e6e6e6"
    readonly property color heartRateColor: "#f80067"

    // All the fonts are given for the window of certain size.
    // Resizing the window changes all the fonts accordingly
    readonly property int defaultSize: 500
    readonly property real fontScaleFactor: Math.min(wWidth, wHeight) / defaultSize

    // Font sizes
    readonly property real microFontSize: 16 * fontScaleFactor
    readonly property real tinyFontSize: 20 * fontScaleFactor
    readonly property real smallFontSize: 24 * fontScaleFactor
    readonly property real mediumFontSize: 32 * fontScaleFactor
    readonly property real bigFontSize: 36 * fontScaleFactor
    readonly property real largeFontSize: 54 * fontScaleFactor
    readonly property real hugeFontSize: 128 * fontScaleFactor

    // Some other values
    property real fieldHeight: wHeight * 0.08
    property real fieldMargin: fieldHeight * 0.5
    property real buttonHeight: wHeight * 0.08
    property real buttonRadius: buttonHeight * 0.1

    // Some help functions
    function heightForWidth(w, ss) {
        return w / ss.width * ss.height
    }
}
