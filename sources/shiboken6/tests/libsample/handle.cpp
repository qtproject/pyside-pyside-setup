// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "handle.h"

SAMPLE_HANDLE HandleHolder::createHandle()
{
    return (SAMPLE_HANDLE) new OBJ;
}

bool HandleHolder::compare(HandleHolder *other)
{
    return other->m_handle == m_handle;
}

bool HandleHolder::compare2(HandleHolder *other)
{
    return other->m_handle2 == m_handle2;
}
