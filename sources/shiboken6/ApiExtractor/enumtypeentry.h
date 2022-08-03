// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ENUMTYPEENTRY_H
#define ENUMTYPEENTRY_H

#include "typesystem.h"

class EnumTypeEntryPrivate;
class EnumValueTypeEntry;
class FlagsTypeEntry;

class EnumTypeEntry : public TypeEntry
{
public:
    explicit EnumTypeEntry(const QString &entryName,
                           const QVersionNumber &vr,
                           const TypeEntry *parent);

    TypeSystem::PythonEnumType pythonEnumType() const;
    void setPythonEnumType(TypeSystem::PythonEnumType t);

    QString targetLangQualifier() const;

    QString qualifier() const;

    const EnumValueTypeEntry *nullValue() const;
    void setNullValue(const EnumValueTypeEntry *n);

    void setFlags(FlagsTypeEntry *flags);
    FlagsTypeEntry *flags() const;

    bool isEnumValueRejected(const QString &name) const;
    void addEnumValueRejection(const QString &name);
    QStringList enumValueRejections() const;

    TypeEntry *clone() const override;
#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    explicit EnumTypeEntry(EnumTypeEntryPrivate *d);
};

#endif // ENUMTYPEENTRY_H
