// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CTORCONVRULE_H
#define CTORCONVRULE_H

#include "libsamplemacros.h"

class CtorConvRule
{
public:
    LIBMINIMAL_DEFAULT_COPY_MOVE(CtorConvRule)

    explicit CtorConvRule(long value) noexcept : m_value(value) {}
    virtual ~CtorConvRule() = default;
    virtual void dummyVirtualMethod() {}
    long value() { return m_value; }
private:
    long m_value;
};

#endif
