// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HANDLE_H
#define HANDLE_H

#include "libsamplemacros.h"

/* See http://bugs.pyside.org/show_bug.cgi?id=1105. */
namespace Foo {
    using SAMPLE_HANDLE = unsigned long;
}

class LIBSAMPLE_API OBJ
{
};

using SAMPLE_HANDLE = OBJ *;

class LIBSAMPLE_API HandleHolder
{
public:
    explicit HandleHolder(SAMPLE_HANDLE ptr = nullptr) : m_handle(ptr) {}
    explicit HandleHolder(Foo::SAMPLE_HANDLE val): m_handle2(val) {}

    void set(SAMPLE_HANDLE ptr);
    inline void set(const Foo::SAMPLE_HANDLE &val) { m_handle2 = val; }
    inline SAMPLE_HANDLE handle() { return m_handle; }
    inline Foo::SAMPLE_HANDLE handle2() { return m_handle2; }

    static SAMPLE_HANDLE createHandle();
    bool compare(HandleHolder *other);
    bool compare2(HandleHolder *other);

private:
    SAMPLE_HANDLE m_handle;
    Foo::SAMPLE_HANDLE m_handle2;
};

inline void HandleHolder::set(SAMPLE_HANDLE)
{
    SAMPLE_HANDLE tmp = m_handle;
    m_handle = tmp;
}

struct LIBSAMPLE_API PrimitiveStruct {};
using PrimitiveStructPtr = struct PrimitiveStruct *;
struct LIBSAMPLE_API PrimitiveStructPointerHolder
{
    PrimitiveStructPtr primitiveStructPtr;
};

#endif // HANDLE_H
