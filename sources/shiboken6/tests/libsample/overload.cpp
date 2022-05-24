// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "overload.h"

Overload::FunctionEnum Overload::overloaded()
{
    return Function0;
}

Overload::FunctionEnum Overload::overloaded(Size* size)
{
    return Function1;
}

Overload::FunctionEnum Overload::overloaded(Point* point, ParamEnum param)
{
    return Function2;
}

Overload::FunctionEnum Overload::overloaded(const Point& point)
{
    return Function3;
}

