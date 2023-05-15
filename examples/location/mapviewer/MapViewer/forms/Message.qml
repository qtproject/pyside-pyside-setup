// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

MessageForm {
    property string title
    property string message
    property variant backPage

    signal closeForm(variant backPage)

    button.onClicked: {
        closeForm(backPage)
    }

    Component.onCompleted: {
        messageText.text = message
        messageTitle.text = title
    }
}
