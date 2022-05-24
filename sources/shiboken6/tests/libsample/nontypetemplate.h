// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NONTYPETEMPLATE_H
#define NONTYPETEMPLATE_H

#include "libsamplemacros.h"

#include <algorithm>
#include <numeric>

template <int Size> class IntArray
{
public:
    explicit IntArray(const int *data) { std::copy(data, data + Size, m_array); }
    explicit IntArray(int v) { std::fill(m_array, m_array + Size, v); }

    int sum() const { return std::accumulate(m_array, m_array + Size, int(0)); }

private:
    int m_array[Size];
};

typedef IntArray<2> IntArray2;
typedef IntArray<3> IntArray3;

#endif // NONTYPETEMPLATE_H
