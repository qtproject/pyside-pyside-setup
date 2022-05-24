// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
