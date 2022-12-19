// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "oddbool.h"

ComparisonTester::ComparisonTester(int v) : m_value(v)
{
}

ComparisonTester &ComparisonTester::operator=(int v)
{
    m_value = v;
    return *this;
}

int ComparisonTester::compare(const ComparisonTester &rhs) const
{
    if (m_value < rhs.m_value)
        return -1;
    if (m_value > rhs.m_value)
        return 1;
    return 0;
}

SpaceshipComparisonTester::SpaceshipComparisonTester(int v) : m_value(v)
{
}
