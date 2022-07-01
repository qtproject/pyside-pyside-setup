// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef STDUNIQUEPTRTESTBENCH_H
#define STDUNIQUEPTRTESTBENCH_H

#include "libsmartmacros.h"

#include <memory>

class Integer;
namespace Smart {
class Integer2;
}

class LIB_SMART_API StdUniquePtrTestBench
{
public:
    StdUniquePtrTestBench();
    ~StdUniquePtrTestBench();

    static std::unique_ptr<Integer> createInteger(int v = 42);
    static std::unique_ptr<Integer> createNullInteger();
    static void printInteger2(const std::unique_ptr<Smart::Integer2> &p);
    static void printInteger(const std::unique_ptr<Integer> &p);
    static void takeInteger(std::unique_ptr<Integer> p); // Call with std::move()

    static std::unique_ptr<int> createInt(int v = 42);
    static std::unique_ptr<int> createNullInt();
    static void printInt(const std::unique_ptr<int> &p);
    static void takeInt(std::unique_ptr<int> p); // Call with std::move()
};

class LIB_SMART_API StdUniquePtrVirtualMethodTester
{
public:
    StdUniquePtrVirtualMethodTester();
    virtual ~StdUniquePtrVirtualMethodTester();

    bool testModifyIntegerByRef(int value, int expectedValue);
    bool testModifyIntegerValue(int value, int expectedValue);
    bool testCreateInteger(int value, int expectedValue);

protected:
    virtual std::unique_ptr<Integer> doCreateInteger(int v);
    virtual int doModifyIntegerByRef(const std::unique_ptr<Integer> &p);
    virtual int doModifyIntegerByValue(std::unique_ptr<Integer> p);
};

#endif // STDUNIQUEPTRTESTBENCH_H
