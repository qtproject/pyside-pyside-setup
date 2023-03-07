// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtLocation
import QtPositioning

RouteAddressForm {
    property alias plugin : tempGeocodeModel.plugin;
    property variant fromAddress;
    property variant toAddress;
    signal showMessage(string topic, string message)
    signal showRoute(variant startCoordinate,variant endCoordinate)
    signal closeForm()

    goButton.onClicked: {
        tempGeocodeModel.reset()
        fromAddress.country =  fromCountry.text
        fromAddress.street = fromStreet.text
        fromAddress.city =  fromCity.text
        toAddress.country = toCountry.text
        toAddress.street = toStreet.text
        toAddress.city = toCity.text
        tempGeocodeModel.startCoordinate = QtPositioning.coordinate()
        tempGeocodeModel.endCoordinate = QtPositioning.coordinate()
        tempGeocodeModel.query = fromAddress
        tempGeocodeModel.update();
        goButton.enabled = false;
    }

    clearButton.onClicked: {
        fromStreet.text = ""
        fromCity.text = ""
        fromCountry.text = ""
        toStreet.text = ""
        toCity.text = ""
        toCountry.text = ""
    }

    cancelButton.onClicked: {
        closeForm()
    }

    Component.onCompleted: {
        fromStreet.text  = fromAddress.street
        fromCity.text =  fromAddress.city
        fromCountry.text = fromAddress.country
        toStreet.text = toAddress.street
        toCity.text = toAddress.city
        toCountry.text = toAddress.country
    }

    GeocodeModel {
        id: tempGeocodeModel

        property int success: 0
        property variant startCoordinate
        property variant endCoordinate

        onCountChanged: {
            if (success == 1 && count == 1) {
                query = toAddress
                update();
            }
        }

        onStatusChanged: {
            if ((status == GeocodeModel.Ready) && (count == 1)) {
                success++
                if (success == 1) {
                    startCoordinate.latitude = get(0).coordinate.latitude
                    startCoordinate.longitude = get(0).coordinate.longitude
                }
                if (success == 2) {
                    endCoordinate.latitude = get(0).coordinate.latitude
                    endCoordinate.longitude = get(0).coordinate.longitude
                    success = 0
                    if (startCoordinate.isValid && endCoordinate.isValid)
                        showRoute(startCoordinate,endCoordinate)
                    else
                        goButton.enabled = true
                }
            } else if ((status == GeocodeModel.Ready) || (status == GeocodeModel.Error)) {
                var st = (success == 0 ) ? "start" : "end"
                success = 0
                if ((status == GeocodeModel.Ready) && (count == 0 )) {
                    showMessage(qsTr("Geocode Error"),qsTr("Unsuccessful geocode"));
                    goButton.enabled = true;
                }
                else if (status == GeocodeModel.Error) {
                    showMessage(qsTr("Geocode Error"),
                                qsTr("Unable to find location for the") + " " +
                                st + " " +qsTr("point"))
                    goButton.enabled = true;
                }
                else if ((status == GeocodeModel.Ready) && (count > 1 )) {
                    showMessage(qsTr("Ambiguous geocode"),
                                count + " " + qsTr("results found for the") +
                                " " + st + " " +qsTr("point, please specify location"))
                    goButton.enabled = true;
                }
            }
        }
    }
}
