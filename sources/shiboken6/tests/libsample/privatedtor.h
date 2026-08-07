// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PRIVATEDTOR_H
#define PRIVATEDTOR_H

#include "libsamplemacros.h"

class PrivateDtor
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(PrivateDtor)

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

// PYSIDE-504: Force a wrapper when using --avoid-protected-hack.
// This only works for MSVC (see comment at HeaderGenerator::protectedHackDefine)
#ifdef _MSC_VER
protected:
#endif
    inline int protectedInstanceCalls() { return m_instantiations; }

private:
    int m_instantiations = 0;

    PrivateDtor() noexcept = default;
    ~PrivateDtor() = default;
};

#endif // PRIVATEDTOR_H
