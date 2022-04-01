/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
