// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "complex.h"

#include <iostream>

Complex::Complex(double real, double imag)
    : m_real(real), m_imag(imag)
{
}

Complex Complex::operator+(const Complex &other)
{
    Complex result;
    result.setReal(m_real + other.real());
    result.setImaginary(m_imag + other.imag());
    return result;
}

void Complex::show() const
{
    std::cout << "(real: " << m_real << ", imag: " << m_imag << ")";
}
