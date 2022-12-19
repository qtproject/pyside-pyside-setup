// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef REMOVEDNAMESPACE_H
#define REMOVEDNAMESPACE_H

#include "libsamplemacros.h"

namespace RemovedNamespace1
{

enum RemovedNamespace1_Enum { RemovedNamespace1_Enum_Value0 = 0,
                              RemovedNamespace1_Enum_Value1 = 1 };

enum { RemovedNamespace1_AnonymousEnum_Value0 };

inline int mathSum(int x, int y) { return x + y; }

struct ObjectOnInvisibleNamespace
{
    bool exists() const { return true; }
    static int toInt(RemovedNamespace1_Enum e) { return static_cast<int>(e); }
    static ObjectOnInvisibleNamespace consume(const ObjectOnInvisibleNamespace &other) { return other; }
};

namespace RemovedNamespace2
{

enum RemovedNamespace2_Enum { RemovedNamespace2_Enum_Value0 };

} // namespace RemovedNamespace2
} // namespace RemovedNamespace1

namespace UnremovedNamespace
{

namespace RemovedNamespace3
{
    enum RemovedNamespace3_Enum { RemovedNamespace3_Enum_Value0 };

    enum { RemovedNamespace3_AnonymousEnum_Value0 };

    inline int nestedMathSum(int x, int y) { return x + y; }

} // namespace RemovedNamespace3
} // namespace UnremovedNamespace

#endif // REMOVEDNAMESPACE_H
