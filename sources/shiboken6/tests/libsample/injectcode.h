// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef INJECTCODE_H
#define INJECTCODE_H

#include "libsamplemacros.h"

#include <utility>
#include <string>

class LIBSAMPLE_API InjectCode
{
public:
    InjectCode();
    virtual ~InjectCode();

    const char *simpleMethod1(int arg0, int arg1);
    const char *simpleMethod2();
    const char *simpleMethod3(int argc, char **argv);

   const char *overloadedMethod(int argc, char **argv);
    const char *overloadedMethod(int arg0, double arg1);
    const char *overloadedMethod(int arg0, bool arg1);

    virtual int arrayMethod(int count, int *values) const;
    inline int callArrayMethod(int count, int *values) const { return arrayMethod(count, values); }
    virtual const char *virtualMethod(int arg);
    int sumArrayAndLength(int *values) const;

private:
    // This attr is just to retain the memory pointed by all return values,
    // So, the memory returned by all methods will be valid until someone call
    // another method of this class.
    std::string m_valueHolder;

    template<typename T>
    const char *toStr(const T &value);
};

#endif // INJECTCODE_H

