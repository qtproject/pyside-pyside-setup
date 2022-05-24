// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "typesystypedef.h"

ValueWithUnitUser::ValueWithUnitUser() = default;

ValueWithUnit<double, LengthUnit::Millimeter>
    ValueWithUnitUser::doubleInchToMillimeter(ValueWithUnit<double, LengthUnit::Inch> v)
{
    return ValueWithUnit<double, LengthUnit::Millimeter>(v.value() * 254);
}
