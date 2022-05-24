// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PRIVATEDTOR_H
#define PRIVATEDTOR_H

#include "libsamplemacros.h"

class PrivateDtor
{
public:
    inline static PrivateDtor* instance()
    {
        static PrivateDtor self;
        self.m_instanciations++;
        return &self;
    }

    inline int instanceCalls()
    {
        return m_instanciations;
    }

protected:
    inline int protectedInstanceCalls() { return m_instanciations; }

private:
    int m_instanciations;

    PrivateDtor() : m_instanciations(0) {}
    PrivateDtor(const PrivateDtor&) {}
    ~PrivateDtor() {}
};

#endif
