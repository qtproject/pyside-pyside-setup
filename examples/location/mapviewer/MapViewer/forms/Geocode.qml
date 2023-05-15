// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtPositioning

GeocodeForm {

    property variant address
    signal showPlace(variant address)
    signal closeForm()

    goButton.onClicked: {
        // fill out the Address element
        address.street = street.text
        address.city = city.text
        address.state = stateName.text
        address.country = country.text
        address.postalCode = postalCode.text
        showPlace(address)
    }

    clearButton.onClicked: {
        street.text = ""
        city.text = ""
        stateName.text = ""
        country.text = ""
        postalCode.text = ""
    }

    cancelButton.onClicked: {
        closeForm()
    }

    Component.onCompleted: {
        street.text = address.street
        city.text = address.city
        stateName.text = address.state
        country.text = address.country
        postalCode.text = address.postalCode
    }
}
