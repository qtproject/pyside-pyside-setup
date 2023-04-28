// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import People

BirthdayParty {
    id: theParty

    HappyBirthdaySong on announcement { name: theParty.host.name }

    onPartyStarted: (time) => { console.log("This party started rockin' at " + time); }

    host: Boy {
        name: "Bob Jones"
        shoe_size: 12
    }

    Boy {
        name: "Leo Hodges"
        BirthdayParty.rsvp: "2009-07-06"
    }
    Boy {
        name: "Jack Smith"
    }
    Girl {
        name: "Anne Brown"
        BirthdayParty.rsvp: "2009-07-01"
    }
}
