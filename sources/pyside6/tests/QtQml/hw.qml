// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

Rectangle {
     id: page
     width: 500; height: 200
     color: "lightgray"

     Text {
         id: helloText
         text: "Hello world!"
         y: 30
         anchors.horizontalCenter: page.horizontalCenter
         font.pointSize: 24; font.bold: true
     }

     Image {
         // It's okay for this to fail.
         source: "http://localhost/logo.png"
     }
}
