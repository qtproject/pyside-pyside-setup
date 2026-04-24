// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKDESTRUCTORENTRY_H
#define SBKDESTRUCTORENTRY_H

extern "C"
{
using ObjectDestructor = void (*)(void *);
}

namespace Shiboken
{

/// Data required to invoke a C++ destructor
struct DestructorEntry
{
    ObjectDestructor destructor;
    void *cppInstance;
};

} // namespace Shiboken

#endif // SBKDESTRUCTORENTRY_H
