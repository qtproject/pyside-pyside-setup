// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "multiple_derived.h"

MDerived1::MDerived1() noexcept = default;

MDerived2::MDerived2() noexcept = default;

MDerived3::MDerived3() noexcept = default;

MDerived4::MDerived4() noexcept = default;

MDerived5::MDerived5() noexcept = default;

MDerived1 *MDerived1::transformFromBase1(Base1 *self)
{
    return dynamic_cast<MDerived1*>(self);
}

MDerived1 *MDerived1::transformFromBase2(Base2 *self)
{
    return dynamic_cast<MDerived1*>(self);
}
