/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

#ifndef INTWRAPPER_H
#define INTWRAPPER_H

#include "libsamplemacros.h"

// Wrapper around int for testing operators
class LIBSAMPLE_API IntWrapper
{
public:
    constexpr explicit IntWrapper(int i) noexcept : m_number(i) {}
    int toInt() const;

    IntWrapper &operator++();
    IntWrapper operator++(int); // Postfix

    IntWrapper &operator--();
    IntWrapper operator--(int); // Postfix

    friend constexpr inline bool operator==(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number == rhs.m_number; }
    friend constexpr inline bool operator!=(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number != rhs.m_number; }
    friend constexpr inline bool operator<(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number < rhs.m_number; }
    friend constexpr inline bool operator>(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number > rhs.m_number; }
    friend constexpr inline bool operator<=(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number <= rhs.m_number; }
    friend constexpr inline bool operator>=(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return lhs.m_number >= rhs.m_number; }

    constexpr inline IntWrapper &operator+=(IntWrapper i);
    constexpr inline IntWrapper &operator-=(const IntWrapper i);

    friend constexpr inline IntWrapper operator+(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return IntWrapper(lhs.m_number + rhs.m_number); }
    friend constexpr inline IntWrapper operator-(IntWrapper lhs, IntWrapper  rhs) noexcept
    { return IntWrapper(lhs.m_number - rhs.m_number); }

    // FIXME: Test spaceship operator with C++ 20:
    // auto operator<=>(IntWrapper) const = default;

private:
    int m_number;
};

constexpr inline IntWrapper &IntWrapper::operator+=(IntWrapper i)
{
    m_number += i.m_number;
    return *this;
}

constexpr inline IntWrapper &IntWrapper::operator-=(const IntWrapper i)
{
    m_number -= i.m_number;
    return *this;
}

#endif // INTWRAPPER_H
