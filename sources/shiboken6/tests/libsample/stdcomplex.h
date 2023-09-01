// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef STDCOMPLEX_H
#define STDCOMPLEX_H

#include "libsamplemacros.h"

#include <complex>
#include <iosfwd>

// A complex number based on std::complex for exercising esoteric number
// protocols (Py_nb_). For standard number protocols, see Point.

class LIBSAMPLE_API StdComplex
{
    using Impl = std::complex<double>;

public:
    StdComplex() noexcept;
    explicit StdComplex(double re, double img) noexcept;

    double real() const { return m_impl.real(); }
    double imag() const { return m_impl.imag(); }

    double abs_value() const { return std::abs(m_impl); } // abs() is reserved Python word

    StdComplex pow(const StdComplex &exp) const;

    operator double() const { return abs_value(); }
    operator int() const;

    friend inline bool operator==(const StdComplex &c1, const StdComplex &c2) noexcept
    { return c1.m_impl == c2.m_impl; }
    friend inline bool operator!=(const StdComplex &c1, const StdComplex &c2) noexcept
    { return c1.m_impl != c2.m_impl; }

    friend inline StdComplex operator+(const StdComplex &c1, const StdComplex &c2) noexcept
    { return StdComplex(c1.m_impl + c2.m_impl); }
    friend inline StdComplex operator-(const StdComplex &c1, const StdComplex &c2) noexcept
    { return StdComplex(c1.m_impl - c2.m_impl); }
    friend inline StdComplex operator*(const StdComplex &c1, const StdComplex &c2) noexcept
    { return StdComplex(c1.m_impl * c2.m_impl); }
    friend inline StdComplex operator/(const StdComplex &c1, const StdComplex &c2) noexcept
    { return StdComplex(c1.m_impl / c2.m_impl); }

private:
    explicit StdComplex(const Impl &impl) noexcept;

    Impl m_impl;
};

std::ostream &operator<<(std::ostream &str, const StdComplex &c);

#endif // STDCOMPLEX_H
