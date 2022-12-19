// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "strlist.h"

#include <algorithm>

bool StrList::operator==(const std::list<Str> &other) const
{
    return size() == other.size()
        && std::equal(begin(), end(), other.begin());
}

Str StrList::join(const Str &sep) const
{
    Str result;
    const auto i1 = begin();
    const auto i2 = end();
    for (auto it = i1; i1 != i2; ++it) {
        if (it != i1)
            result.append(sep);
        result.append(*it);
    }
    return result;
}
