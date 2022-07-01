// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "stduniqueptrtestbench.h"
#include "smart_integer.h"

#include <iostream>

std::ostream &operator<<(std::ostream &str, const std::unique_ptr<Integer> &p)
{
    str << "unique_ptr<Integer>(";
    if (p.get())
        str << p->value();
    else
        str << "nullptr";
    str << ')';
    return str;
}

std::ostream &operator<<(std::ostream &str, const std::unique_ptr<Smart::Integer2> &p)
{
    str << "unique_ptr<Integer>(";
    if (p.get())
        str << p->value();
    else
        str << "nullptr";
    str << ')';
    return str;
}

std::ostream &operator<<(std::ostream &str, const std::unique_ptr<int> &p)
{
    str << "unique_ptr<int>(";
    if (p.get())
        str << *p;
    else
        str << "nullptr";
    str << ')';
    return str;
}

StdUniquePtrTestBench::StdUniquePtrTestBench() = default;
StdUniquePtrTestBench::~StdUniquePtrTestBench() = default;

std::unique_ptr<Integer> StdUniquePtrTestBench::createInteger(int v)
{
    auto result = std::make_unique<Integer>();
    result->setValue(v);
    return result;
}

std::unique_ptr<Integer> StdUniquePtrTestBench::createNullInteger()
{
    return {};
}

void StdUniquePtrTestBench::printInteger(const std::unique_ptr<Integer> &p)
{
    std::cerr << __FUNCTION__ << ' ' << p << '\n';
}

void StdUniquePtrTestBench::takeInteger(std::unique_ptr<Integer> p)
{
    std::cerr << __FUNCTION__ << ' ' << p << '\n';
}

std::unique_ptr<int> StdUniquePtrTestBench::createInt(int v)
{
    return std::make_unique<int>(v);
}

std::unique_ptr<int> StdUniquePtrTestBench::createNullInt()
{
    return {};
}

void StdUniquePtrTestBench::printInt(const std::unique_ptr<int> &p)
{
    std::cerr << __FUNCTION__ << ' ' << p << '\n';
}

void StdUniquePtrTestBench::takeInt(std::unique_ptr<int> p)
{
    std::cerr << __FUNCTION__ << ' ' << p << '\n';
}

StdUniquePtrVirtualMethodTester::StdUniquePtrVirtualMethodTester() = default;

StdUniquePtrVirtualMethodTester::~StdUniquePtrVirtualMethodTester() = default;

bool StdUniquePtrVirtualMethodTester::testModifyIntegerByRef(int value, int expectedValue)
{
     auto p = std::make_unique<Integer>();
     p->setValue(value);
     const int actualValue = doModifyIntegerByRef(p);
     return p.get() != nullptr && actualValue == expectedValue;
}

bool StdUniquePtrVirtualMethodTester::testModifyIntegerValue(int value, int expectedValue)
{
    auto p = std::make_unique<Integer>();
    p->setValue(value);
    const int actualValue = doModifyIntegerByValue(std::move(p));
    return p.get() == nullptr && actualValue == expectedValue;
}

bool StdUniquePtrVirtualMethodTester::testCreateInteger(int value, int expectedValue)
{
    auto p = doCreateInteger(value);
    return p.get() != nullptr && p->value() == expectedValue;
}

std::unique_ptr<Integer> StdUniquePtrVirtualMethodTester::doCreateInteger(int v)
{
    auto result = std::make_unique<Integer>();
    result->setValue(v);
    return result;
}

int StdUniquePtrVirtualMethodTester::doModifyIntegerByRef(const std::unique_ptr<Integer> &p)
{
    return p->value() + 1;
}

int StdUniquePtrVirtualMethodTester::doModifyIntegerByValue(std::unique_ptr<Integer> p)
{
    return p->value() + 1;
}

void StdUniquePtrTestBench::printInteger2(const std::unique_ptr<Smart::Integer2> &p)
{
    std::cerr << __FUNCTION__ << ' ' << p << '\n';
}
