// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NONDEFAULTCTOR_H
#define NONDEFAULTCTOR_H

#include "libsamplemacros.h"

class NonDefaultCtor
{
public:
    NonDefaultCtor(int value) : m_value(value)
    {
    }

    virtual ~NonDefaultCtor() = default;

    inline int value() const
    {
        return m_value;
    }

    inline NonDefaultCtor returnMyself()
    {
        return *this;
    }

    inline NonDefaultCtor returnMyself(int)
    {
        return *this;
    }

    inline NonDefaultCtor returnMyself(int, NonDefaultCtor)
    {
        return *this;
    }

    virtual NonDefaultCtor returnMyselfVirtual()
    {
        return *this;
    }

    inline NonDefaultCtor callReturnMyselfVirtual()
    {
        return returnMyselfVirtual();
    }

private:
    int m_value;
};

#endif // NONDEFAULTCTOR_H
