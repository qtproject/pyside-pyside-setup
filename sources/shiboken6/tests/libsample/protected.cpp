// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "protected.h"

int ProtectedVirtualDestructor::dtor_called = 0;

const char *ProtectedNonPolymorphic::dataTypeName(void *) const
{
    return "pointer";
}

const char *ProtectedNonPolymorphic::dataTypeName(int) const
{
    return "integer";
}
