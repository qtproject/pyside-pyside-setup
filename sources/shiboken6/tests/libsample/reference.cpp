// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "reference.h"

using namespace std;

void
Reference::show() const
{
    cout << "Reference.objId: " << m_objId << ", address: " << this;
}

int
Reference::usesReferenceVirtual(Reference& r, int inc)
{
    return r.m_objId + inc;
}

int
Reference::usesConstReferenceVirtual(const Reference& r, int inc)
{
    return r.m_objId + inc;
}

int
Reference::callUsesReferenceVirtual(Reference& r, int inc)
{
    return usesReferenceVirtual(r, inc);
}

int
Reference::callUsesConstReferenceVirtual(const Reference& r, int inc)
{
    return usesConstReferenceVirtual(r, inc);
}

void
Reference::alterReferenceIdVirtual(Reference& r)
{
    r.setObjId(r.objId() * Reference::multiplier());
}

void
Reference::callAlterReferenceIdVirtual(Reference& r)
{
    alterReferenceIdVirtual(r);
}

ObjTypeReference::~ObjTypeReference()
{
}
