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
    Echo() = default;
    ~Echo() = default;

    void doNothingWithConstBool(const bool hi);
    void methodWithNamedArg(const Str &string = Str{});

    Str operator()(const Str &s, const int i) { return s + i; }

    // These method are here just for compilation test purposes
    Echo &operator<<(unsigned int item);
    Echo &operator<<(signed int item);
    Echo &operator<<(const ObjectType *item);
    Echo &operator<<(Str str);
};

inline void Echo::doNothingWithConstBool(const bool)
{
}

inline void Echo::methodWithNamedArg(const Str &)
{
}

inline Echo &Echo::operator<<(unsigned int)
{
    return *this;
}

inline Echo &Echo::operator<<(signed int)
{
    return *this;
}

inline Echo &Echo::operator<<(const ObjectType *)
{
    return *this;
}

inline Echo &Echo::operator<<(Str)
{
    return *this;
}

#endif // ECHO_H
