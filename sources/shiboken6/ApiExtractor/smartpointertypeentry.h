// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMARTPOINTERTYPEENTRY_H
#define SMARTPOINTERTYPEENTRY_H

#include "complextypeentry.h"

class SmartPointerTypeEntryPrivate;

struct SmartPointerInstantiation
{
    QString name; // user defined name
    TypeEntryCPtr typeEntry;
};

class SmartPointerTypeEntry : public ComplexTypeEntry
{
public:
    using Instantiations = QList<SmartPointerInstantiation>;

    explicit SmartPointerTypeEntry(const QString &entryName,
                                   const QString &getterName,
                                   TypeSystem::SmartPointerType type,
                                   const QString &refCountMethodName,
                                   const QVersionNumber &vr,
                                   const TypeEntryCPtr &parent);

    TypeSystem::SmartPointerType smartPointerType() const;

    QString getter() const;

    QString refCountMethodName() const;

    QString valueCheckMethod() const;
    void setValueCheckMethod(const QString &);
    QString nullCheckMethod() const;
    void setNullCheckMethod(const QString &);
    QString resetMethod() const;
    void setResetMethod(const QString &);

    TypeEntry *clone() const override;

    const Instantiations &instantiations() const;
    void setInstantiations(const Instantiations &i);
    bool matchesInstantiation(const TypeEntryCPtr &e) const;

    QString getTargetName(const AbstractMetaType &metaType) const;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    SmartPointerTypeEntry(SmartPointerTypeEntryPrivate *d);
};

#endif // SMARTPOINTERTYPEENTRY_H
