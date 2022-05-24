// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "multiple_derived.h"

MDerived1::MDerived1() : m_value(100)
{
}

MDerived2::MDerived2() : m_value(200)
{
}

MDerived3::MDerived3() : m_value(3000)
{
}

MDerived4::MDerived4()
{
}

MDerived5::MDerived5()
{
}

MDerived1*
MDerived1::transformFromBase1(Base1* self)
{
    MDerived1* ptr = dynamic_cast<MDerived1*>(self);
    return ptr;
}

MDerived1*
MDerived1::transformFromBase2(Base2* self)
{
    MDerived1* ptr = dynamic_cast<MDerived1*>(self);
    return ptr;
}

