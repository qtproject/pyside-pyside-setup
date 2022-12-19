// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NOIMPLICITCONVERSION_H
#define NOIMPLICITCONVERSION_H

#include "libsamplemacros.h"

// This class must not have implicit conversions AND
// no conversion operators should be defined in its own module.
class NoImplicitConversion
{
public:
    explicit NoImplicitConversion(int objId) : m_objId(objId) {}
    inline int objId() const { return m_objId; }
    inline static int receivesNoImplicitConversionByValue(NoImplicitConversion arg)
    { return arg.m_objId; }
    inline static int receivesNoImplicitConversionByPointer(NoImplicitConversion *arg)
    { return arg->m_objId; }
    inline static int receivesNoImplicitConversionByReference(NoImplicitConversion &arg)
    { return arg.m_objId; }
private:
    int m_objId;
};

#endif // NOIMPLICITCONVERSION_H

