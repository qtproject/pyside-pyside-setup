// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ENUMVALUETYPEENTRY_H
#define ENUMVALUETYPEENTRY_H

#include "typesystem.h"

class EnumTypeEntry;
class EnumValueTypeEntryPrivate;

// EnumValueTypeEntry is used for resolving integer type templates
// like array<EnumValue>. Note: Dummy entries for integer values will
// be created for non-type template parameters, where m_enclosingEnum==nullptr.
class EnumValueTypeEntry : public TypeEntry
{
public:
    explicit EnumValueTypeEntry(const QString& name, const QString& value,
                                const EnumTypeEntryCPtr &enclosingEnum,
                                bool isScopedEnum, const QVersionNumber &vr);

    QString value() const;
    EnumTypeEntryCPtr enclosingEnum() const;

    TypeEntry *clone() const override;

protected:
    explicit EnumValueTypeEntry(EnumValueTypeEntryPrivate *d);
};

#endif // ENUMVALUETYPEENTRY_H
