// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SNAKECASETEST_H
#define SNAKECASETEST_H

#include "libsamplemacros.h"

LIBSAMPLE_API int SnakeCaseGlobalFunction();

class LIBSAMPLE_API SnakeCaseTest
{
public:
    SnakeCaseTest();
    virtual ~SnakeCaseTest();

    int testFunction1() const;
    int testFunctionDisabled() const;
    int testFunctionBoth() const;

    int callVirtualFunc() const;

    int testField = 42;
    int testFieldDisabled = 42;
    int testFieldBoth = 42;

protected:
    virtual int virtualFunc() const;
};

class LIBSAMPLE_API SnakeCaseDerivedTest : public SnakeCaseTest
{
public:
    SnakeCaseDerivedTest();

protected:
    int virtualFunc() const override;
};

#endif // SNAKECASETEST_H
