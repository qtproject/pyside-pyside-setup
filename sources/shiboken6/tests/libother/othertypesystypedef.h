// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OTHERTYPESYSTYPEDEF_H
#define OTHERTYPESYSTYPEDEF_H

#include "libothermacros.h"

#include <typesystypedef.h>

class LIBOTHER_API OtherValueWithUnitUser
{
public:
    OtherValueWithUnitUser();

    static ValueWithUnit<double, LengthUnit::Inch> doubleMillimeterToInch(ValueWithUnit<double, LengthUnit::Millimeter>);

    static ValueWithUnit<int, LengthUnit::Inch> intMillimeterToInch(ValueWithUnit<int, LengthUnit::Millimeter>);
};

#endif // OTHERTYPESYSTYPEDEF_H
