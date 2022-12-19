// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPEHOLDER_H
#define OBJECTTYPEHOLDER_H

#include "libsamplemacros.h"
#include "objecttype.h"
#include "str.h"

class LIBSAMPLE_API ObjectTypeHolder
{
public:
    explicit ObjectTypeHolder(const char *objectName);
    explicit ObjectTypeHolder(const ObjectType *object = ObjectType::defaultInstance());
    virtual ~ObjectTypeHolder();

    const ObjectType *getObjectType() const { return m_objectType; }

    virtual Str passObjectTypeAsReference(const ObjectType &objectType);
    Str callPassObjectTypeAsReference();

private:
   const ObjectType *m_objectType;
};

#endif // OBJECTTYPEHOLDER_H
