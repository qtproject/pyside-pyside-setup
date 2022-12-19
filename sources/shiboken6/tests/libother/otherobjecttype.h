// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OTHEROBJECTTYPE_H
#define OTHEROBJECTTYPE_H

#include "libothermacros.h"
#include "objecttype.h"
#include "collector.h"
#include "samplenamespace.h"
#include "removednamespaces.h"

class LIBOTHER_API OtherObjectType : public ObjectType
{
public:
    static int enumAsInt(SampleNamespace::SomeClass::PublicScopedEnum value);
    static int enumAsIntForInvisibleNamespace(RemovedNamespace1::RemovedNamespace1_Enum value);
};

LIBOTHER_API Collector &operator<<(Collector &, const OtherObjectType &);

#endif // OTHEROBJECTTYPE_H
