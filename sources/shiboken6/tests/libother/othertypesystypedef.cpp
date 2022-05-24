// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "othertypesystypedef.h"

OtherValueWithUnitUser::OtherValueWithUnitUser() = default;


ValueWithUnit<double, LengthUnit::Inch>
    OtherValueWithUnitUser::doubleMillimeterToInch(ValueWithUnit<double, LengthUnit::Millimeter> v)
{
    return ValueWithUnit<double, LengthUnit::Inch>(v.value() / 254);
}

ValueWithUnit<int, LengthUnit::Inch>
    OtherValueWithUnitUser::intMillimeterToInch(ValueWithUnit<int, LengthUnit::Millimeter> v)
{
    return ValueWithUnit<int, LengthUnit::Inch>(v.value() / 254);
}
