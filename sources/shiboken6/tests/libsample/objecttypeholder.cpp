// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objecttypeholder.h"

ObjectTypeHolder::ObjectTypeHolder(const char *objectName)
{
    auto object = new ObjectType();
    object->setObjectName(objectName);
    m_objectType = object;
}

ObjectTypeHolder::ObjectTypeHolder(const ObjectType *object) :
    m_objectType(object)
{
}

ObjectTypeHolder::~ObjectTypeHolder()
{
    delete m_objectType;
}

Str ObjectTypeHolder::passObjectTypeAsReference(const ObjectType &objectType)
{
    return objectType.objectName();
}

Str ObjectTypeHolder::callPassObjectTypeAsReference()
{
    return passObjectTypeAsReference(*m_objectType);
}
