// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DELETEDDTOR_H
#define DELETEDDTOR_H

#include "libsamplemacros.h"

class DeletedDtor
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(DeletedDtor)

    DeletedDtor() noexcept = default;
    ~DeletedDtor() = delete;

    int value() const { return 42; }
};

#endif // DELETEDDTOR_H
