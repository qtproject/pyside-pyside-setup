// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VALUETYPEENTRY_H
#define VALUETYPEENTRY_H

#include "complextypeentry.h"

class ValueTypeEntry : public ComplexTypeEntry
{
public:
    explicit ValueTypeEntry(const QString &entryName, const QVersionNumber &vr,
                            const TypeEntry *parent);

    bool isValue() const override;

    TypeEntry *clone() const override;

protected:
    explicit ValueTypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                            const TypeEntry *parent);
    explicit ValueTypeEntry(ComplexTypeEntryPrivate *d);
};

#endif // VALUETYPEENTRY_H
