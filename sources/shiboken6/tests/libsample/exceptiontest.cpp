// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "exceptiontest.h"

class TestException : public std::exception
{
public:
    const char *what() const noexcept override
    { return "TestException"; }
};

ExceptionTest::ExceptionTest() = default;

int ExceptionTest::intThrowStdException(bool doThrow)
{
    if (doThrow)
        throw TestException();
    return 1;
}

void ExceptionTest::voidThrowStdException(bool doThrow)
{
    if (doThrow)
        throw TestException();
}

int ExceptionTest::intThrowInt(bool doThrow)
{
    if (doThrow)
        throw 42;
    return 1;
}

void ExceptionTest::voidThrowInt(bool doThrow)
{
    if (doThrow)
        throw 42;
}

ExceptionTest *ExceptionTest::create(bool doThrow)
{
    if (doThrow)
        throw TestException();
    return new ExceptionTest;
}
