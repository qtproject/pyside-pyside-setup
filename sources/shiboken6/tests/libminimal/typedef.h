// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEDEF_H
#define TYPEDEF_H

#include "libminimalmacros.h"

#include <vector>

// Test wrapping of a typedef
using MyArrayInt = std::vector<int>;

LIBMINIMAL_API bool arrayFuncInt(std::vector<int> a);
LIBMINIMAL_API bool arrayFuncIntTypedef(MyArrayInt a);

LIBMINIMAL_API std::vector<int> arrayFuncIntReturn(int size);
LIBMINIMAL_API MyArrayInt arrayFuncIntReturnTypedef(int size);

// Test wrapping of a typedef of a typedef
using MyArray = MyArrayInt;

LIBMINIMAL_API bool arrayFunc(std::vector<int> a);
LIBMINIMAL_API bool arrayFuncTypedef(MyArray a);

LIBMINIMAL_API std::vector<int> arrayFuncReturn(int size);
LIBMINIMAL_API MyArray arrayFuncReturnTypedef(int size);

#endif
