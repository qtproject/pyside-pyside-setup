// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTMODEL_H
#define OBJECTMODEL_H

#include "objecttype.h"
#include "libsamplemacros.h"

class LIBSAMPLE_API ObjectModel : public ObjectType
{
public:
    explicit ObjectModel(ObjectType *parent = nullptr)
        : ObjectType(parent) {}

    void setData(ObjectType *data);
    virtual ObjectType *data() const;

    // The MethodCalled enum and related static methods were created to
    // test bug #630 [http://bugs.openbossa.org/show_bug.cgi?id=630]
    enum MethodCalled { ObjectTypeCalled, ObjectModelCalled };
    static MethodCalled receivesObjectTypeFamily(const ObjectType &object);
    static MethodCalled receivesObjectTypeFamily(const ObjectModel &object);

private:
    // The model holds only one piece of data.
    // (This is just a test after all.)
    ObjectType *m_data = nullptr;
};

#endif // OBJECTMODEL_H
