// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMARTPTRTESTER_H
#define SMARTPTRTESTER_H

#include "libothermacros.h"

#include <smart.h>
#include <str.h>

class LIBOTHER_API SmartPtrTester
{
public:
    SharedPtr<Str> createSharedPtrStr(const char *what);
    std::string valueOfSharedPtrStr(const SharedPtr<Str> &);

    SharedPtr<Integer> createSharedPtrInteger(int v);
    int valueOfSharedPtrInteger(const SharedPtr<Integer> &);

    void fiddleInt(const SharedPtr<int> &);
};

#endif // SMARTPTRTESTER_H
