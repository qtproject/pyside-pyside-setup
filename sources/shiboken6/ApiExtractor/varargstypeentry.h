// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VARARGSTYPEENTRY_H
#define VARARGSTYPEENTRY_H

#include "typesystem.h"

class VarargsTypeEntry : public TypeEntry
{
public:
    VarargsTypeEntry();

    TypeEntry *clone() const override;

protected:
    explicit VarargsTypeEntry(TypeEntryPrivate *d);
};

#endif // VARARGSTYPEENTRY_H
