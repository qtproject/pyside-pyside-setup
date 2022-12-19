// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "otherderived.h"

OtherDerived::OtherDerived(int id) : Abstract(id)
{
}

OtherDerived::~OtherDerived() = default;

Abstract *OtherDerived::createObject()
{
    static int id = 100;
    return new OtherDerived(id++);
}

void OtherDerived::pureVirtual()
{
}

void *OtherDerived::pureVirtualReturningVoidPtr()
{
    return nullptr;
}

void OtherDerived::unpureVirtual()
{
}

void OtherDerived::pureVirtualPrivate()
{
}
