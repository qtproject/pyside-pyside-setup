// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OVERLOADSORT_H
#define OVERLOADSORT_H

#include "libsamplemacros.h"

#include <list>

class ImplicitTarget
{
public:
    ImplicitTarget() = default;
};

class ImplicitBase
{
public:
    ImplicitBase() = default;
    ImplicitBase(const ImplicitTarget &b);
};

inline ImplicitBase::ImplicitBase(const ImplicitTarget &)
{
}

class LIBSAMPLE_API SortedOverload
{
public:

    const char *overload(int x);
    const char *overload(double x);
    const char *overload(ImplicitBase x);
    const char *overload(ImplicitTarget x);
    const char *overload(const std::list<ImplicitBase> &x);

    int implicit_overload(const ImplicitBase &x);

    const char *overloadDeep(int x, ImplicitBase &y);

    inline const char *pyObjOverload(int, int) { return "int,int"; }
    inline const char *pyObjOverload(unsigned char *, int)
    { return "PyObject,int"; }
};

class LIBSAMPLE_API CustomOverloadSequence
{
public:
    int overload(short v) const;
    int overload(int v) const;
};

#endif // OVERLOADSORT_H
