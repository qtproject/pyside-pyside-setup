// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONNECTION_H
#define CONNECTION_H

#include "pysidetest_macros.h"

// PYSIDE-2792, testing converter name clashes with QMetaObject::Connection.
class Connection
{
public:
    Connection(int handle = 0) noexcept : m_handle(handle) {}

    int handle() const { return m_handle; }

private:
    int m_handle;
};

#endif // CONNECTION_H
