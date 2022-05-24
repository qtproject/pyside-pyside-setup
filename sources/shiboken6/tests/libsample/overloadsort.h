// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OVERLOADSORT_H
#define OVERLOADSORT_H

#include "libsamplemacros.h"

#include <list>

class ImplicitTarget
{
public:
    ImplicitTarget(){}
};

class ImplicitBase
{
public:
    ImplicitBase(){}
    ImplicitBase(const ImplicitTarget &b){}
};

class SortedOverload
{
public:

    inline const char *overload(int x) {
        return "int";
    }

    inline const char *overload(double x) {
        return "double";
    }

    inline const char *overload(ImplicitBase x) {
        return "ImplicitBase";
    }

    inline const char *overload(ImplicitTarget x) {
        return "ImplicitTarget";
    }

    inline const char *overload(const std::list<ImplicitBase> &x) {
        return "list(ImplicitBase)";
    }

    inline int implicit_overload(const ImplicitBase &x) {
        return 1;
    }

    inline const char *overloadDeep(int x, ImplicitBase &y) {
        return "ImplicitBase";
    }


    inline const char* pyObjOverload(int, int) { return "int,int"; }
    inline const char* pyObjOverload(unsigned char*, int) { return "PyObject,int"; }

};

class LIBSAMPLE_API CustomOverloadSequence
{
public:
    int overload(short v) const;
    int overload(int v) const;
};

#endif // OVERLOADSORT_H

