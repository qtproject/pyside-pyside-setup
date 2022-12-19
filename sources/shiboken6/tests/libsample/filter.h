// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FILTER_H
#define FILTER_H

#include "libsamplemacros.h"

#include <string>
#include <list>

class Intersection;

class LIBSAMPLE_API Filter
{
};

class LIBSAMPLE_API Data : public Filter
{
public:
    enum Field {
        Name,
        Album,
        Year
    };

    explicit Data(Field field, std::string value);

    Field field() const { return m_field; }
    std::string value() const { return m_value; }

private:
    Field m_field;
    std::string m_value;
};

class LIBSAMPLE_API Union : public Filter
{
public:

    Union(const Data &);
    Union(const Intersection &);
    Union() = default;

    std::list<Filter> filters() const { return m_filters; }
    void addFilter(const Filter &data) { m_filters.push_back(data); }

private:
    std::list<Filter> m_filters;
};

class LIBSAMPLE_API Intersection : public Filter
{
public:
    Intersection(const Data &);
    Intersection(const Union &);
    Intersection() = default;

    std::list<Filter> filters() const { return m_filters; }
    void addFilter(const Filter &data) { m_filters.push_back(data); }

private:
    std::list<Filter> m_filters;
};

LIBSAMPLE_API Intersection operator&(const Intersection &a, const Intersection &b);

#endif // FILTER_H


