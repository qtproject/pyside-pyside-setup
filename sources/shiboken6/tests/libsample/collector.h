// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef COLLECTOR_H
#define COLLECTOR_H

#include "libsamplemacros.h"
#include "intwrapper.h"
#include "objecttype.h"

#include <list>

class LIBSAMPLE_API Collector
{
public:
    Collector() = default;
    virtual ~Collector() = default;
    Collector(const Collector &) = delete;
    Collector &operator=(const Collector &) = delete;

    void clear();

    Collector &operator<<(ObjectType::Identifier item);

    Collector &operator<<(const ObjectType *);

    std::list<ObjectType::Identifier> items();
    int size() const;

private:
    std::list<ObjectType::Identifier> m_items;
};

/* Helper for testing external operators */
LIBSAMPLE_API Collector &operator<<(Collector &, const IntWrapper &);

#endif // COLLECTOR_H

