// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "otherobjecttype.h"

Collector &operator<<(Collector &collector, const OtherObjectType &obj)
{
    collector << obj.identifier() * 2;
    return collector;
}

int OtherObjectType::enumAsInt(SampleNamespace::SomeClass::PublicScopedEnum value)
{
    return static_cast<int>(value);
}

int OtherObjectType::enumAsIntForInvisibleNamespace(RemovedNamespace1::RemovedNamespace1_Enum value)
{
    return static_cast<int>(value);
}
