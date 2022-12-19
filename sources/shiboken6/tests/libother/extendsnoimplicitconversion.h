// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef EXTENDSNOIMPLICITCONVERSION_H
#define EXTENDSNOIMPLICITCONVERSION_H

#include "libothermacros.h"
#include "noimplicitconversion.h"

class ExtendsNoImplicitConversion
{
public:
    explicit ExtendsNoImplicitConversion(int objId) : m_objId(objId) {};
    inline int objId() const { return m_objId; }
    inline operator NoImplicitConversion() const { return NoImplicitConversion(m_objId); }

private:
    int m_objId;
};

#endif // EXTENDSNOIMPLICITCONVERSION_H
