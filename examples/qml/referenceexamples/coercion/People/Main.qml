// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import People

BirthdayParty {
    host: Boy {
        name: "Bob Jones"
        shoe_size: 12
    }
    guests: [
        Boy { name: "Leo Hodges" },
        Boy { name: "Jack Smith" },
        Girl { name: "Anne Brown" }
    ]
}
