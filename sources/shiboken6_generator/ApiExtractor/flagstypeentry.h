// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FLAGSTYPEENTRY_H
#define FLAGSTYPEENTRY_H

#include "cpptypeentry.h"

class EnumTypeEntry;
class FlagsTypeEntryPrivate;

// FlagsTypeEntry is configurable for global flags only
class FlagsTypeEntry : public CppTypeEntry
{
public:
    explicit FlagsTypeEntry(const QString &entryName, const QVersionNumber &vr,
                            const TypeEntryCPtr &parent);

    QString originalName() const;
    void setOriginalName(const QString &s);

    QString flagsName() const;
    void setFlagsName(const QString &name);

    EnumTypeEntryPtr originator() const;
    void setOriginator(const EnumTypeEntryPtr &e);

    TypeEntry *clone() const override;

    void formatDebug(QDebug &debug) const override;

protected:
    explicit FlagsTypeEntry(FlagsTypeEntryPrivate *d);

    QString buildTargetLangName() const override;
};

#endif // FLAGSTYPEENTRY_H
