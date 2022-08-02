// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef EXCEPTIONTEST_H
#define EXCEPTIONTEST_H

#include "libsamplemacros.h"

#include <exception>

class LIBSAMPLE_API ExceptionTest
{
  public:
    ExceptionTest();

    int intThrowStdException(bool doThrow);
    void voidThrowStdException(bool doThrow);

    int intThrowInt(bool doThrow);
    void voidThrowInt(bool doThrow);

    static ExceptionTest *create(bool doThrow);
};

#endif // EXCEPTIONTEST_H
