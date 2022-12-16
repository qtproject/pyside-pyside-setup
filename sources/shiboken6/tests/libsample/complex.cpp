// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "complex.h"

Complex::Complex(double real, double imag)
    : m_real(real), m_imag(imag)
{
}

Complex
Complex::operator+(Complex& other)
{
    Complex result;
    result.setReal(m_real + other.real());
    result.setImaginary(m_imag + other.imag());
    return result;
}

void
Complex::show()
{
    std::cout << "(real: " << m_real << ", imag: " << m_imag << ")";
}


