// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtPositioning

RouteCoordinateForm {
    property variant toCoordinate
    property variant fromCoordinate
    signal showRoute(variant startCoordinate,variant endCoordinate)
    signal closeForm()

    goButton.onClicked: {
        var startCoordinate = QtPositioning.coordinate(parseFloat(fromLatitude.text),
                                                       parseFloat(fromLongitude.text));
        var endCoordinate = QtPositioning.coordinate(parseFloat(toLatitude.text),
                                                     parseFloat(toLongitude.text));
        if (startCoordinate.isValid && endCoordinate.isValid) {
           goButton.enabled = false;
           showRoute(startCoordinate,endCoordinate)
        }
    }

    clearButton.onClicked: {
        fromLatitude.text = ""
        fromLongitude.text = ""
        toLatitude.text = ""
        toLongitude.text  = ""
    }

    cancelButton.onClicked: {
        closeForm()
    }

    Component.onCompleted: {
        fromLatitude.text = "" + fromCoordinate.latitude
        fromLongitude.text = "" + fromCoordinate.longitude
        toLatitude.text = "" + toCoordinate.latitude
        toLongitude.text = "" + toCoordinate.longitude
    }
}
