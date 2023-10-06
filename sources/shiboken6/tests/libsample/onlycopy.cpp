// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "onlycopy.h"

class OnlyCopyPrivate
{
public:
    explicit OnlyCopyPrivate(int v = 0) : value(v) {}

    int value;
};

OnlyCopy::OnlyCopy(int value) : d(std::make_shared<OnlyCopyPrivate>(value))
{
}

OnlyCopy::~OnlyCopy() = default;

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
