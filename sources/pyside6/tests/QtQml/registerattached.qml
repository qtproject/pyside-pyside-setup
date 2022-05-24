// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import TestLayouts

TestLayout {
    id: layout

    widgets: [
        TestWidget {
            id: widget1
            TestLayout.leftMargin: 10
        },

        TestWidget {
            id: widget2
            TestLayout.leftMargin: 20
        }
    ]
}
