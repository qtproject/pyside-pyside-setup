// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "abstract.h"

#include <iostream>

const int Abstract::staticPrimitiveField = 0;

Abstract::Abstract(int id) : m_id(id)
{
    bitField = 0;
}

Abstract::~Abstract() = default;

void Abstract::unpureVirtual()
{
}

void Abstract::callUnpureVirtual()
{
    this->unpureVirtual();
}

void Abstract::callPureVirtual()
{
    this->pureVirtual();
}

void Abstract::show(PrintFormat format) const
{
    std::cout << '<';
    switch(format) {
    case Short:
        std::cout << this;
        break;
    case Verbose:
        std::cout << "class " << className() << " | cptr: " << this
                  << ", id: " << m_id;
        break;
    case OnlyId:
        std::cout << "id: " << m_id;
        break;
    case ClassNameAndId:
        std::cout << className() << " - id: " << m_id;
        break;
    }
    std::cout << '>';
}

void Abstract::callVirtualGettingEnum(PrintFormat p)
{
    virtualGettingAEnum(p);
}

void Abstract::virtualGettingAEnum(Abstract::PrintFormat)
{
}
