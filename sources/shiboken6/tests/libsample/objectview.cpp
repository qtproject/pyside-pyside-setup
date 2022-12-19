// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objectview.h"
#include "objectmodel.h"
#include "str.h"

Str ObjectView::displayModelData()
{
    if (!m_model)
        return Str("(NULL)");
    return Str("Name: %VAR").arg(m_model->objectName());
}

void ObjectView::modifyModelData(Str &data)
{
    if (m_model)
        m_model->setObjectName(data);
}

ObjectType *ObjectView::getRawModelData()
{
    return m_model->data();
}
