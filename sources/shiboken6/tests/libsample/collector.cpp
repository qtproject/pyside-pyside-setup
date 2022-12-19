// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "collector.h"

void Collector::clear()
{
    m_items.clear();
}

Collector &Collector::operator<<(ObjectType::Identifier item)
{
    m_items.push_back(item);
    return *this;
}

Collector &Collector::operator<<(const ObjectType *obj)
{
    m_items.push_back(obj->identifier());
    return *this;
}

std::list<ObjectType::Identifier> Collector::items()
{
    return m_items;
}

int Collector::size() const
{
    return int(m_items.size());
}

Collector &operator<<(Collector &s, const IntWrapper &w)
{
    s << w.toInt();
    return s;
}
