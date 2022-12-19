// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PRIVATEDTOR_H
#define PRIVATEDTOR_H

#include "libsamplemacros.h"

class PrivateDtor
{
public:
    inline static PrivateDtor *instance()
    {
        static PrivateDtor self;
        self.m_instantiations++;
        return &self;
    }

    inline int instanceCalls()
    {
        return m_instantiations;
    }

protected:
    inline int protectedInstanceCalls() { return m_instantiations; }

private:
    int m_instantiations = 0;

    PrivateDtor() = default;
    PrivateDtor(const PrivateDtor &) = default;
    ~PrivateDtor() = default;
};

#endif // PRIVATEDTOR_H
