// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "smartptrtester.h"

SharedPtr<Str> SmartPtrTester::createSharedPtrStr(const char *what)
{
    return SharedPtr<Str>(new Str(what));
}

std::string SmartPtrTester::valueOfSharedPtrStr(const SharedPtr<Str> &str)
{
    return str->cstring();
}

SharedPtr<Integer> SmartPtrTester::createSharedPtrInteger(int v)
{
    auto i = SharedPtr<Integer>(new Integer);
    i->m_int = v;
    return i;
}

int SmartPtrTester::valueOfSharedPtrInteger(const SharedPtr<Integer> &v)
{
    return v->m_int;
}

void SmartPtrTester::fiddleInt(const SharedPtr<int> &) // no binding, should not cause errors
{
}
