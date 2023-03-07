// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import "../helper.js" as Helper

//! [routeinfomodel0]
ListView {
//! [routeinfomodel0]
    property variant routeModel
    property string totalTravelTime
    property string totalDistance
    signal closeForm()
//! [routeinfomodel1]
    interactive: true
    model: ListModel { id: routeInfoModel }
    header: RouteListHeader {}
    delegate:  RouteListDelegate{
        routeIndex.text: index + 1
        routeInstruction.text: instruction
        routeDistance.text: distance
    }
//! [routeinfomodel1]
    footer: Button {
        anchors.horizontalCenter: parent.horizontalCenter
        text: qsTr("Close")
        onClicked: {
            closeForm()
        }
    }

    Component.onCompleted: {
        //! [routeinfomodel2]
        routeInfoModel.clear()
        if (routeModel.count > 0) {
            for (var i = 0; i < routeModel.get(0).segments.length; i++) {
                routeInfoModel.append({
                    "instruction": routeModel.get(0).segments[i].maneuver.instructionText,
                     "distance": Helper.formatDistance(routeModel.get(0).segments[i].maneuver.distanceToNextInstruction)
                });
            }
        }
        //! [routeinfomodel2]
        totalTravelTime = routeModel.count == 0 ? "" : Helper.formatTime(routeModel.get(0).travelTime)
        totalDistance = routeModel.count == 0 ? "" : Helper.formatDistance(routeModel.get(0).distance)
    }
//! [routeinfomodel3]
}
//! [routeinfomodel3]
