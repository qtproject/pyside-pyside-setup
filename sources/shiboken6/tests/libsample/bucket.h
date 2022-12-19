// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef BUCKET_H
#define BUCKET_H

#include "libsamplemacros.h"
#include "objecttype.h"

#include <list>

class ObjectType;

class LIBSAMPLE_API Bucket : public ObjectType
{
public:
    Bucket() = default;
    void push(int);
    int pop();
    bool empty();
    void lock();
    inline bool locked() { return m_locked; }
    void unlock();

    virtual bool virtualBlockerMethod();
    inline bool callVirtualBlockerMethodButYouDontKnowThis() { return virtualBlockerMethod(); }

private:
    std::list<int> m_data;

    volatile bool m_locked = false;
};

#endif // BUCKET_H
