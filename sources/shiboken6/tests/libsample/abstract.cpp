// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "abstract.h"
#include "objecttype.h"

using namespace std;

const int Abstract::staticPrimitiveField = 0;

Abstract::Abstract(int id) : m_id(id)
{
    toBeRenamedField = readOnlyField = primitiveField = 123;
    valueTypeField = Point(12, 34);
    objectTypeField = nullptr;
    bitField = 0;
}

Abstract::~Abstract()
{
}

void
Abstract::unpureVirtual()
{
}

void
Abstract::callUnpureVirtual()
{
    this->unpureVirtual();
}


void
Abstract::callPureVirtual()
{
    this->pureVirtual();
}

void
Abstract::show(PrintFormat format)
{
    cout << '<';
    switch(format) {
        case Short:
            cout << this;
            break;
        case Verbose:
            cout << "class " << className() << " | cptr: " << this;
            cout << ", id: " << m_id;
            break;
        case OnlyId:
            cout << "id: " << m_id;
            break;
        case ClassNameAndId:
            cout << className() << " - id: " << m_id;
            break;
    }
    cout << '>';
}

void Abstract::callVirtualGettingEnum(PrintFormat p)
{
    virtualGettingAEnum(p);
}

void Abstract::virtualGettingAEnum(Abstract::PrintFormat)
{
}

