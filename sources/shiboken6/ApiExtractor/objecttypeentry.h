// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPEENTRY_H
#define OBJECTTYPEENTRY_H

#include "complextypeentry.h"

class ObjectTypeEntry : public ComplexTypeEntry
{
public:
    explicit ObjectTypeEntry(const QString &entryName, const QVersionNumber &vr,
                             const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

protected:
    explicit ObjectTypeEntry(ComplexTypeEntryPrivate *d);
};

#endif // OBJECTTYPEENTRY_H
