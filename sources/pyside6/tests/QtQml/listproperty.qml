// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick 2.0
import test.ListPropertyTest

Rectangle {
    width: 360
    height: 360

    Person {
        id: person
        friends: [
            Person{
                name: "Alice"
            },
            Person{
                name: "Bob"
            },
            Person{
                name: "Charlie"
            }
        ]
    }

    Person{
        id: david
        name: "David"
    }

    Component.onCompleted: {
        // Access the length of the list
        console.log("List length: " + person.friends.length);

        // Access the first element of the list
        console.log("First element: " + person.friends[0].name);

        // Remove the last item of the list
        console.log("Removing last item: " + person.friends.pop().name);

        // Repalce the last item of the list
        console.log("Replacing last item: " + person.friends[person.friends.length - 1].name);
        person.friends[person.friends.length - 1] = david;
        console.log("Replaced last item: " + person.friends[person.friends.length - 1].name);

        // Clear the list
        person.friends = [];
        console.log("List length after clearing: " + person.friends.length);
    }
}
