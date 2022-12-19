// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "number.h"

#include <sstream>

Str Number::toStr() const
{
    std::ostringstream in;
    in << m_value;
    return in.str().c_str();
}

Point operator*(const Point &p, const Number &n)
{
    return Point(p.x() * n.value(), p.y() * n.value());
}

Complex Number::toComplex() const
{
    return Complex(m_value);
}

Number Number::fromComplex(Complex cpx)
{
    return Number(cpx.real());
}
