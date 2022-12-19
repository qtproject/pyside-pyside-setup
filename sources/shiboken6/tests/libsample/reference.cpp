// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "reference.h"

#include <iostream>

void Reference::show() const
{
    std::cout << "Reference.objId: " << m_objId << ", address: " << this;
}

Reference &Reference::returnMySecondArg(int, Reference &ref)
{
    return ref;
}

int Reference::usesReferenceVirtual(Reference &r, int inc)
{
    return r.m_objId + inc;
}

int Reference::usesConstReferenceVirtual(const Reference &r, int inc)
{
    return r.m_objId + inc;
}

int Reference::callUsesReferenceVirtual(Reference &r, int inc)
{
    return usesReferenceVirtual(r, inc);
}

int Reference::callUsesConstReferenceVirtual(const Reference &r, int inc)
{
    return usesConstReferenceVirtual(r, inc);
}

void Reference::alterReferenceIdVirtual(Reference &r)
{
    r.setObjId(r.objId() * Reference::multiplier());
}

void Reference::callAlterReferenceIdVirtual(Reference &r)
{
    alterReferenceIdVirtual(r);
}

ObjTypeReference::~ObjTypeReference() = default;

ObjTypeReference &ObjTypeReference::returnMySecondArg(int, ObjTypeReference &ref)
{
    return ref;
}
