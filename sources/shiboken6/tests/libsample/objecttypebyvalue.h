// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPEBYVALUE_H
#define OBJECTTYPEBYVALUE_H

#include "protected.h"

#include <list>

class ObjectTypeByValue
{
public:
    ObjectTypeByValue returnSomeKindOfMe() { return ObjectTypeByValue(); }
    void acceptKindOfMeAsValue(ObjectTypeByValue kindOfMe);

    void acceptListOfObjectTypeByValue(std::list<ObjectTypeByValue> listOfMe);

    // prop used to check for segfaults
    ProtectedProperty prop;
};

inline void ObjectTypeByValue::acceptKindOfMeAsValue(ObjectTypeByValue)
{
}

inline void ObjectTypeByValue::acceptListOfObjectTypeByValue(std::list<ObjectTypeByValue>)
{
}

#endif // OBJECTTYPEBYVALUE_H
