// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ONLYCOPYCLASS_H
#define ONLYCOPYCLASS_H

#include "libsamplemacros.h"

#include <list>
#include <memory>

// These classes simulate a situation found in QWebEngineHistoryItem.

class OnlyCopyPrivate;

class LIBSAMPLE_API OnlyCopy
{
public:
    LIBMINIMAL_DEFAULT_COPY_MOVE(OnlyCopy)

    ~OnlyCopy();

    int value() const;
    static int getValue(OnlyCopy onlyCopy) { return onlyCopy.value(); }
    static int getValueFromReference(const OnlyCopy &onlyCopy) { return onlyCopy.value(); }

private:
    friend class FriendOfOnlyCopy;

    explicit OnlyCopy(int value);

    std::shared_ptr<OnlyCopyPrivate> d;
};

class LIBSAMPLE_API FriendOfOnlyCopy
{
public:
    static OnlyCopy createOnlyCopy(int value);
    static std::list<OnlyCopy> createListOfOnlyCopy(int quantity);
};

#endif // ONLYCOPYCLASS_H
