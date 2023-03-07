// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

Menu {
    property int currentMarker
    property int markersCount
    signal itemClicked(string item)

    MenuItem {
        text: qsTr("Delete")
        onTriggered: itemClicked("deleteMarker")
    }
    MenuItem {
        text: qsTr("Coordinates")
        onTriggered: itemClicked("getMarkerCoordinate")
    }
    MenuItem {
        text: qsTr("Move to")
        onTriggered: itemClicked("moveMarkerTo")
    }
    MenuItem {
        text: currentMarker < markersCount-2 ? qsTr("Route to next markers")
                                             : qsTr("Route to next marker")
        enabled: currentMarker <= markersCount - 2
        onTriggered: currentMarker < markersCount-2 ? itemClicked("routeToNextPoints")
                                                    : itemClicked("routeToNextPoint")
    }
    MenuItem {
        text: currentMarker < markersCount-2 ? qsTr("Distance to next markers")
                                             : qsTr("Distance to next marker")
        enabled: currentMarker <= markersCount - 2
        onTriggered: currentMarker < markersCount-2 ? itemClicked("distanceToNextPoints")
                                                    : itemClicked("distanceToNextPoint")
    }
}
