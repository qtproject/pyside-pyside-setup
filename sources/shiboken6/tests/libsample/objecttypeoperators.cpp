// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objecttypeoperators.h"

ObjectTypeOperators::ObjectTypeOperators(const std::string key) : m_key(key)
{
}

bool ObjectTypeOperators::operator==(const ObjectTypeOperators &other) const
{
    return m_key == other.m_key;
}

const ObjectTypeOperators &ObjectTypeOperators::operator<(const ObjectTypeOperators &other) const
{
    return m_key < other.m_key ? *this : other;
}

bool operator==(const ObjectTypeOperators *obj, const std::string &str)
{
    return obj->key() == str;
}

bool operator==(const std::string &str, const ObjectTypeOperators *obj)
{
    return str == obj->key();
}

std::string operator+(const ObjectTypeOperators *obj, const std::string &str)
{
    return obj->key() + str;
}

std::string operator+(const std::string &str, const ObjectTypeOperators *obj)
{
    return str + obj->key();
}
