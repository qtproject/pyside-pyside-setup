// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "overloadsort.h"

int CustomOverloadSequence::overload(short v) const
{
    return v + int(sizeof(v));
}

int CustomOverloadSequence::overload(int v) const
{
    return v + 4;
}
