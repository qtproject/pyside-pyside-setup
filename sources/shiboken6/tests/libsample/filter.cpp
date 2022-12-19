// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "filter.h"

Data::Data(Field field, std::string value)
    : m_field(field), m_value(value)
{
}

Union::Union(const Data &filter)
{
    m_filters.push_back(filter);
}

Union::Union(const Intersection &filter)
{
    m_filters.push_back(filter);
}

Intersection::Intersection(const Data &filter)
{
    m_filters.push_back(filter);
}

Intersection::Intersection(const Union &filter)
{
    m_filters.push_back(filter);
}

Intersection operator&(const Intersection &a, const Intersection &b)
{
    Intersection filter;
    filter.addFilter(a);
    filter.addFilter(b);

    return filter;
}
