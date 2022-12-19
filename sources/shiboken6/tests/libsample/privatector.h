// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PRIVATECTOR_H
#define PRIVATECTOR_H

#include "libsamplemacros.h"

class PrivateCtor
{
public:
    inline static PrivateCtor *instance()
    {
        static PrivateCtor self;
        self.m_instantiations++;
        return &self;
    }

    inline int instanceCalls()
    {
        return m_instantiations;
    }

private:
    int m_instantiations = 0;

    PrivateCtor() = default;
};

class DeletedDefaultCtor
{
public:
    DeletedDefaultCtor() = delete;

    DeletedDefaultCtor(const DeletedDefaultCtor &) = default;
    DeletedDefaultCtor(DeletedDefaultCtor &&) = default;
    DeletedDefaultCtor &operator=(const DeletedDefaultCtor &) = default;
    DeletedDefaultCtor &operator=(DeletedDefaultCtor &&) = default;
    ~DeletedDefaultCtor() = default;
};

#endif // PRIVATECTOR_H
