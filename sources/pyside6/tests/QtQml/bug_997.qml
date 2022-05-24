// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

Text {
    required property var owner
    text: owner.name + " " + owner.phone
    Component.onCompleted: {
        owner.newName = owner.name
        Qt.quit()
    }
}
