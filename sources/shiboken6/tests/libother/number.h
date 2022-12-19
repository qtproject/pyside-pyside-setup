// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NUMBER_H
#define NUMBER_H

#include "libothermacros.h"
#include "str.h"
#include "point.h"
#include "complex.h"

class LIBOTHER_API Number
{
public:
    explicit Number(int value) : m_value(value) {};
    inline int value() const { return m_value; }

    Str toStr() const;
    inline operator Str() const { return toStr(); }

    friend LIBOTHER_API Point operator*(const Point &, const Number &);

    Complex toComplex() const;
    static Number fromComplex(Complex cpx);

private:
    int m_value;
};

LIBOTHER_API Point operator*(const Point &, const Number &);

#endif // NUMBER_H
