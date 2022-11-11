// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONSTANTVALUETYPEENTRY_H
#define CONSTANTVALUETYPEENTRY_H

#include "typesystem.h"

// For primitive values, typically to provide a dummy type for
// example the '2' in non-type template 'Array<2>'.
class ConstantValueTypeEntry : public TypeEntry
{
public:
    explicit  ConstantValueTypeEntry(const QString& name,
                                     const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

protected:
    explicit ConstantValueTypeEntry(TypeEntryPrivate *d);
};

#endif // CONSTANTVALUETYPEENTRY_H
