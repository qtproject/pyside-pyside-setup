// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "snakecasetest.h"

int SnakeCaseGlobalFunction()
{
    return 42;
}

SnakeCaseTest::SnakeCaseTest() = default;
SnakeCaseTest::~SnakeCaseTest() = default;

int SnakeCaseTest::testFunction1() const
{
    return 42;
}

int SnakeCaseTest::testFunctionDisabled() const
{
    return 42;
}

int SnakeCaseTest::testFunctionBoth() const
{
    return 42;
}

int SnakeCaseTest::callVirtualFunc() const
{
    return virtualFunc();
}

int SnakeCaseTest::virtualFunc() const
{
    return 42;
}

SnakeCaseDerivedTest::SnakeCaseDerivedTest() = default;

int SnakeCaseDerivedTest::virtualFunc() const
{
    return 43;
}
