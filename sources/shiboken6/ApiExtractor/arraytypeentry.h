// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ARRAYTYPEENTRY_H
#define ARRAYTYPEENTRY_H

#include "typesystem.h"

class ArrayTypeEntryPrivate;

class ArrayTypeEntry : public TypeEntry
{
public:
    explicit ArrayTypeEntry(const TypeEntryCPtr &nested_type, const QVersionNumber &vr,
                            const TypeEntryCPtr &parent);

    void setNestedTypeEntry(const TypeEntryPtr &nested);
    TypeEntryCPtr nestedTypeEntry() const;

    TypeEntry *clone() const override;

protected:
    explicit ArrayTypeEntry(ArrayTypeEntryPrivate *d);

    QString buildTargetLangName() const override;
};

#endif // ARRAYTYPEENTRY_H
