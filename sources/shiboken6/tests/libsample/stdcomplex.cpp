// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "stdcomplex.h"

#include <iostream>

StdComplex::StdComplex() noexcept = default;

StdComplex::StdComplex(double re, double img) noexcept : m_impl(re, img)
{
}

StdComplex::operator int() const
{
    return std::lround(abs_value());
}

StdComplex::StdComplex(const Impl &impl) noexcept : m_impl(impl)
{
}

StdComplex StdComplex::pow(const StdComplex &exp) const
{
    return StdComplex(std::pow(m_impl, exp.m_impl));
}

std::ostream &operator<<(std::ostream &str, const StdComplex &c)
{
    str << "Complex(" << c.real() << ", " << c.imag() << ')';
    return str;
}
