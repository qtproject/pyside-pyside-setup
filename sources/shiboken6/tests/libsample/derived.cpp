// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "derived.h"

using namespace std;

Derived::Derived(int id) : Abstract(id)
{
}

Derived::~Derived()
{
}

Abstract*
Derived::createObject()
{
    static int id = 100;
    return new Derived(id++);
}

void
Derived::pureVirtual()
{
}

void*
Derived::pureVirtualReturningVoidPtr()
{
    return nullptr;
}

void
Derived::unpureVirtual()
{
}

bool
Derived::singleArgument(bool b)
{
    return !b;
}

double
Derived::defaultValue(int n)
{
    return ((double) n) + 0.1;
}

OverloadedFuncEnum
Derived::overloaded(int i, int d)
{
    return OverloadedFunc_ii;
}

OverloadedFuncEnum
Derived::overloaded(double n)
{
    return OverloadedFunc_d;
}

Derived::OtherOverloadedFuncEnum
Derived::otherOverloaded(int a, int b, bool c, double d)
{
    return OtherOverloadedFunc_iibd;
}

Derived::OtherOverloadedFuncEnum
Derived::otherOverloaded(int a, double b)
{
    return OtherOverloadedFunc_id;
}

struct SecretClass : public Abstract {
    virtual void pureVirtual() {}
    virtual void *pureVirtualReturningVoidPtr() { return nullptr; }
    virtual PrintFormat returnAnEnum() { return Short; }
    void hideFunction(HideType*){};
private:
    virtual void pureVirtualPrivate() {}
};

Abstract* Derived::triggerImpossibleTypeDiscovery()
{
    return new SecretClass;
}

struct AnotherSecretClass : public Derived {
};

Abstract* Derived::triggerAnotherImpossibleTypeDiscovery()
{
    return new AnotherSecretClass;
}

void Derived::pureVirtualPrivate()
{
}
