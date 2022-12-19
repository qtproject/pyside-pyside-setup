// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sample.h"

namespace sample
{

sample::sample(int value) : m_value(value)
{
}

int sample::value() const
{
    return m_value;
}

bool operator==(const sample &s1, const sample &s2)
{
    return s1.value() == s2.value();
}
} // namespace sample
