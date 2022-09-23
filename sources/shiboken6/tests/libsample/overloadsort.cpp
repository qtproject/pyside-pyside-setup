// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "overloadsort.h"

const char *SortedOverload::overload(int)
{
    return "int";
}

const char *SortedOverload::overload(double)
{
    return "double";
}

const char *SortedOverload::overload(ImplicitBase)
{
    return "ImplicitBase";
}

const char *SortedOverload::overload(ImplicitTarget)
{
    return "ImplicitTarget";
}

const char *SortedOverload::overload(const std::list<ImplicitBase> &)
{
    return "list(ImplicitBase)";
}

int SortedOverload::implicit_overload(const ImplicitBase &)
{
    return 1;
}

const char *SortedOverload::overloadDeep(int, ImplicitBase &)
{
    return "ImplicitBase";
}

int CustomOverloadSequence::overload(short v) const
{
    return v + int(sizeof(v));
}

int CustomOverloadSequence::overload(int v) const
{
    return v + 4;
}
