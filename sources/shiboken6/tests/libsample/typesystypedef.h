// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTYPEDEF_H
#define TYPESYSTYPEDEF_H

#include "libsamplemacros.h"

enum class LengthUnit { Millimeter, Inch };

template <class T, LengthUnit Unit>
class ValueWithUnit
{
    public:
    explicit ValueWithUnit(T value = {}) : m_value(value) {}

    T value() const { return m_value; }
    void setValue(const T &value) { m_value = value; }

private:
    T m_value;
};

class LIBSAMPLE_API ValueWithUnitUser
{
public:
    ValueWithUnitUser();

    static ValueWithUnit<double, LengthUnit::Millimeter> doubleInchToMillimeter(ValueWithUnit<double, LengthUnit::Inch>);
};

#endif // TYPESYSTYPEDEF_H
