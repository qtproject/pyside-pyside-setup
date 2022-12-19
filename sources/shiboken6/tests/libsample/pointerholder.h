// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef POINTERHOLDER_H
#define POINTERHOLDER_H

#include "libsamplemacros.h"

class PointerHolder
{
public:
    explicit PointerHolder(void *ptr) : m_pointer(ptr) {}
    ~PointerHolder() = default;

    inline void *pointer() const { return m_pointer; }

private:
    void *m_pointer;
};

#endif // POINTERHOLDER_H
