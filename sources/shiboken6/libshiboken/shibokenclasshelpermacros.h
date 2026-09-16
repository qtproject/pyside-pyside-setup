// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SHIBOKENCLASSHELPERMACROS_H
#define SHIBOKENCLASSHELPERMACROS_H

#define LIBSHIBOKEN_DISABLE_COPY(Class) \
    Class(const Class &) = delete;\
    Class &operator=(const Class &) = delete;

#define LIBSHIBOKEN_DISABLE_COPY_MOVE(Class) \
    LIBSHIBOKEN_DISABLE_COPY(Class) \
    Class(Class &&) = delete; \
    Class &operator=(Class &&) = delete;

#endif // SHIBOKENCLASSHELPERMACROS_H
