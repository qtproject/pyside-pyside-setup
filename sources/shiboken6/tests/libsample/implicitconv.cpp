// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "implicitconv.h"

ImplicitConv
ImplicitConv::implicitConvCommon(ImplicitConv implicit)
{
    return implicit;
}

ImplicitConv
ImplicitConv::implicitConvDefault(ImplicitConv implicit)
{
    return implicit;
}

ImplicitConv::ICOverloadedFuncEnum
ImplicitConv::implicitConvOverloading(ImplicitConv implicit, int dummyArg)
{
    return ImplicitConv::OverFunc_Ii;
}

ImplicitConv::ICOverloadedFuncEnum
ImplicitConv::implicitConvOverloading(ImplicitConv implicit, bool dummyArg)
{
    return ImplicitConv::OverFunc_Ib;
}

ImplicitConv::ICOverloadedFuncEnum
ImplicitConv::implicitConvOverloading(int dummyArg)
{
    return ImplicitConv::OverFunc_i;
}

ImplicitConv::ICOverloadedFuncEnum
ImplicitConv::implicitConvOverloading(CtorEnum dummyArg)
{
    return ImplicitConv::OverFunc_C;
}

