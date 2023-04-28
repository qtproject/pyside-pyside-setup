// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import People

BirthdayParty {
    Boy {
        name: "Robert Campbell"
        BirthdayParty.rsvp: "2009-07-01"
    }

    Boy {
        name: "Leo Hodges"
        shoe_size: 10
        BirthdayParty.rsvp: "2009-07-06"
    }

    host: Boy {
        name: "Jack Smith"
        shoe_size: 8
    }
}
