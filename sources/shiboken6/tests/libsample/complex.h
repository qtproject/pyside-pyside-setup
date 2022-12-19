// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef COMPLEX_H
#define COMPLEX_H

#include "libsamplemacros.h"

class LIBSAMPLE_API Complex
{
public:
    Complex(double real = 0.0, double imag = 0.0);
    ~Complex() = default;

    inline double real() const { return m_real; }
    inline void setReal(double real) { m_real = real; }
    inline double imag() const { return m_imag; }
    inline void setImaginary(double imag) { m_imag = imag; }

    Complex operator+(const Complex &other);

    void show() const;

private:
    double m_real;
    double m_imag;
};

#endif // COMPLEX_H

