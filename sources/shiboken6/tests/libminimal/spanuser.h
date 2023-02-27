// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SPANUSER_H
#define SPANUSER_H

#include "libminimalmacros.h"

#if __cplusplus >= 202002L
#  include <span>

using IntSpan3 = std::span<int, 3>;
using IntSpan = std::span<int>;
using ConstIntSpan3 = std::span<const int, 3>;
#endif

struct LIBMINIMAL_API SpanUser
{
    SpanUser();

    static bool enabled();

#if __cplusplus >= 202002L
    static IntSpan3 getIntSpan3();
    static IntSpan getIntSpan();
    static ConstIntSpan3 getConstIntSpan3();
    static IntSpan3 getIntSpan3_OpaqueContainer();

    static int sumIntSpan3(IntSpan3 isp3);
    static int sumIntSpan(IntSpan isp);
    static int sumConstIntSpan3(ConstIntSpan3 ispc3);
#endif // C++ 20
};

#endif // SPANUSER_H
