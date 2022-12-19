// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ONLYCOPYCLASS_H
#define ONLYCOPYCLASS_H

#include "libsamplemacros.h"

#include <list>

// These classes simulate a situation found in QWebEngineHistoryItem.

class OnlyCopyPrivate;

class LIBSAMPLE_API OnlyCopy
{
public:
    OnlyCopy(const OnlyCopy &other);
    OnlyCopy &operator=(const OnlyCopy &other);
    ~OnlyCopy();

    int value() const;
    static int getValue(OnlyCopy onlyCopy) { return onlyCopy.value(); }
    static int getValueFromReference(const OnlyCopy &onlyCopy) { return onlyCopy.value(); }

private:
    OnlyCopyPrivate *d;
    explicit OnlyCopy(int value);
    explicit OnlyCopy(OnlyCopyPrivate *d); // rejected due to unknown OnlyCopyPrivate
    friend class FriendOfOnlyCopy;
};

class LIBSAMPLE_API FriendOfOnlyCopy
{
public:
    static OnlyCopy createOnlyCopy(int value);
    static std::list<OnlyCopy> createListOfOnlyCopy(int quantity);
};

#endif // ONLYCOPYCLASS_H
