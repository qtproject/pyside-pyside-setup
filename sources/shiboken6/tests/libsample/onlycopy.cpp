// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "onlycopy.h"

class OnlyCopyPrivate
{
public:
    explicit OnlyCopyPrivate(int v = 0) : value(v) {}

    int value;
};

OnlyCopy::OnlyCopy(int value) : d(new OnlyCopyPrivate(value))
{
}

OnlyCopy::OnlyCopy(OnlyCopyPrivate *dIn) : d(dIn)
{
}

OnlyCopy::~OnlyCopy()
{
    delete d;
}

OnlyCopy::OnlyCopy(const OnlyCopy &other) : d(new OnlyCopyPrivate(other.value()))
{
}

OnlyCopy &OnlyCopy::operator=(const OnlyCopy &other)
{
    d->value = other.d->value;
    return *this;
}

int OnlyCopy::value() const
{
    return d->value;
}

OnlyCopy FriendOfOnlyCopy::createOnlyCopy(int value)
{
    return OnlyCopy(value);
}

std::list<OnlyCopy> FriendOfOnlyCopy::createListOfOnlyCopy(int quantity)
{
    std::list<OnlyCopy> list;
    for (int i = 0; i < quantity; ++i)
        list.push_back(createOnlyCopy(i));
    return list;
}
