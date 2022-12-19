// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPEOPERATORS_H
#define OBJECTTYPEOPERATORS_H

#include "libsamplemacros.h"

#include <string>

class LIBSAMPLE_API ObjectTypeOperators
{
public:
    explicit ObjectTypeOperators(const std::string key);
    virtual ~ObjectTypeOperators() = default;
    ObjectTypeOperators(ObjectTypeOperators &) = delete;
    ObjectTypeOperators &operator=(ObjectTypeOperators &) = delete;

    bool operator==(const ObjectTypeOperators &other) const;
    const ObjectTypeOperators &operator<(const ObjectTypeOperators &other) const;

    // chaos!
    virtual void operator>(const ObjectTypeOperators &) { m_key.append("operator>"); }

    std::string key() const { return m_key; }

private:
    std::string m_key;
};

LIBSAMPLE_API bool operator==(const ObjectTypeOperators *obj, const std::string &str);
LIBSAMPLE_API bool operator==(const std::string &str, const ObjectTypeOperators *obj);
LIBSAMPLE_API std::string operator+(const ObjectTypeOperators *obj, const std::string &str);
LIBSAMPLE_API std::string operator+(const std::string &str, const ObjectTypeOperators *obj);

#endif // OBJECTTYPEOPERATORS_H
