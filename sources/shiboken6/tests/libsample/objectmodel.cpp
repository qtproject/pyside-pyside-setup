// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objectmodel.h"

void ObjectModel::setData(ObjectType *data)
{
    m_data = data;
}

ObjectType *ObjectModel::data() const
{
    return m_data;
}

ObjectModel::MethodCalled ObjectModel::receivesObjectTypeFamily(const ObjectModel &)
{
    return ObjectModel::ObjectModelCalled;
}

ObjectModel::MethodCalled ObjectModel::receivesObjectTypeFamily(const ObjectType &)
{
    return ObjectModel::ObjectTypeCalled;
}
