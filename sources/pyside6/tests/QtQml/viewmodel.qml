// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

ListView {
    width: 100; height: 100
    anchors.fill: parent

    delegate: Rectangle {
        height: 25
        width: 100
        Text { text: model.modelData.title }
    }
}

