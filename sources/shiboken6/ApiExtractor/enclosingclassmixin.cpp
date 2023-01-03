// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "enclosingclassmixin.h"
#include "abstractmetalang.h"
#include "namespacetypeentry.h"

AbstractMetaClassCPtr EnclosingClassMixin::targetLangEnclosingClass() const
{
    auto result = m_enclosingClass.lock();
    while (result && !NamespaceTypeEntry::isVisibleScope(result->typeEntry()))
        result = result->enclosingClass();
    return result;
}
