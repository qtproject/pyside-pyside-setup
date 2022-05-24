// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ECHO_H
#define ECHO_H

#include "libsamplemacros.h"
#include "str.h"

class ObjectType;

class Echo
{
public:
    Echo(){}
    ~Echo(){}

    void doNothingWithConstBool(const bool hi) {}
    void methodWithNamedArg(const Str& string = Str("")) {}

    Str operator()(const Str& s, const int i) { return s + i; }

    // These method are here just for compilation test purposes
    Echo& operator<<(unsigned int item) { return *this; }
    Echo& operator<<(signed int item) { return *this; }
    Echo& operator<<(const ObjectType* item) { return *this; }
    Echo& operator<<(Str str) { return *this; }
};

#endif
