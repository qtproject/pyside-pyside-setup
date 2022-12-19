// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "injectcode.h"

#include <sstream>

InjectCode::InjectCode() = default;

InjectCode::~InjectCode() = default;

template<typename T>
const char *InjectCode::toStr(const T &value)
{
    std::ostringstream s;
    s << value;
    m_valueHolder = s.str();
    return m_valueHolder.c_str();
}

const char *InjectCode::simpleMethod1(int arg0, int arg1)
{
    return toStr(arg0 + arg1);
}

const char *InjectCode::simpleMethod2()
{
    return "_";
}

const char *InjectCode::simpleMethod3(int argc, char **argv)
{
    for (int i = 0; i < argc; ++i)
        m_valueHolder += argv[i];
    return m_valueHolder.c_str();
}

const char *InjectCode::overloadedMethod(int arg0, bool arg1)
{
    toStr(arg0);
    m_valueHolder += arg1 ? "true" : "false";
    return m_valueHolder.c_str();
}

const char *InjectCode::overloadedMethod(int arg0, double arg1)
{
    return toStr(arg0 + arg1);
}

const char *InjectCode::overloadedMethod(int argc, char **argv)
{
    return simpleMethod3(argc, argv);
}

const char *InjectCode::virtualMethod(int arg)
{
    return toStr(arg);
}

int InjectCode::arrayMethod(int count, int *values) const
{
    int ret = 0;
    for (int i=0; i < count; i++)
        ret += values[i];
    return ret;
}

int InjectCode::sumArrayAndLength(int *values) const
{
    int sum = 0;

    while (*values) {
        sum = sum + *values + 1;
        ++values;
    }

    return sum;
}
