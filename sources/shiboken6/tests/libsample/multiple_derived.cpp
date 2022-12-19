// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "multiple_derived.h"

MDerived1::MDerived1() = default;

MDerived2::MDerived2() = default;

MDerived3::MDerived3() = default;

MDerived4::MDerived4() = default;

MDerived5::MDerived5() = default;

MDerived1 *MDerived1::transformFromBase1(Base1 *self)
{
    return dynamic_cast<MDerived1*>(self);
}

MDerived1 *MDerived1::transformFromBase2(Base2 *self)
{
    return dynamic_cast<MDerived1*>(self);
}
