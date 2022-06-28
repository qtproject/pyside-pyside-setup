// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "stdsharedptrtestbench.h"
#include "smart_integer.h"

#include <iostream>

StdSharedPtrTestBench::StdSharedPtrTestBench() = default;
StdSharedPtrTestBench::~StdSharedPtrTestBench() = default;

std::shared_ptr<Integer> StdSharedPtrTestBench::createInteger(int v)
{
    auto result = std::make_shared<Integer>();
    result->setValue(v);
    return result;
}

std::shared_ptr<Integer> StdSharedPtrTestBench::createNullInteger()
{
    return {};
}

void StdSharedPtrTestBench::printInteger(const std::shared_ptr<Integer> &p)
{
    std::cerr << __FUNCTION__ << ' ';
    if (p.get())
        std::cerr << p->value();
    else
        std::cerr << "nullptr";
    std::cerr << '\n';
}

std::shared_ptr<int> StdSharedPtrTestBench::createInt(int v)
{
    return std::make_shared<int>(v);
}

std::shared_ptr<int> StdSharedPtrTestBench::createNullInt()
{
    return {};
}

void StdSharedPtrTestBench::printInt(const std::shared_ptr<int> &p)
{
    std::cerr << __FUNCTION__ << ' ';
    if (p.get())
        std::cerr << *p;
    else
        std::cerr << "nullptr";
    std::cerr << '\n';
}

StdSharedPtrVirtualMethodTester::StdSharedPtrVirtualMethodTester() = default;
StdSharedPtrVirtualMethodTester::~StdSharedPtrVirtualMethodTester() = default;

std::shared_ptr<Integer> StdSharedPtrVirtualMethodTester::callModifyInteger(const std::shared_ptr<Integer> &p)
{
    return doModifyInteger(p);
}

std::shared_ptr<Integer> StdSharedPtrVirtualMethodTester::doModifyInteger(std::shared_ptr<Integer> p)
{
    p->setValue(p->value() + 1);
    return p;
}
