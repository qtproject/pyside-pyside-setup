// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "stdoptionaltestbench.h"

#include <iostream>

std::ostream &operator<<(std::ostream &str, const Integer &i)
{
    str << i.value();
    return str;
}

template <class T>
std::ostream &operator<<(std::ostream &str, const std::optional<T> &o)
{
    if (o.has_value())
        str << o.value();
    else
        str << "nullopt";
    return str;
}

StdOptionalTestBench::StdOptionalTestBench() = default;

std::optional<int> StdOptionalTestBench::optionalInt() const
{
    return m_optionalInt;
}

void StdOptionalTestBench::setOptionalInt(const std::optional<int> &i)
{
    std::cout << __FUNCTION__ << ' ' << i << '\n';
    m_optionalInt = i;
}

void StdOptionalTestBench::setOptionalIntValue(int i)
{
    std::cout << __FUNCTION__ << ' ' << i << '\n';
    m_optionalInt.emplace(i);
}

std::optional<Integer> StdOptionalTestBench::optionalInteger() const
{
    return m_optionalInteger;
}

void StdOptionalTestBench::setOptionalInteger(const std::optional<Integer> &s)
{
    std::cout << __FUNCTION__ << ' ' << s << '\n';
    m_optionalInteger = s;
}

void StdOptionalTestBench::setOptionalIntegerValue(Integer &s)
{
    std::cout << __FUNCTION__ << ' ' << s << '\n';
    m_optionalInteger.emplace(s);
}
