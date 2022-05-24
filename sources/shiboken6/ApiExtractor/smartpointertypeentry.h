// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMARTPOINTERTYPEENTRY_H
#define SMARTPOINTERTYPEENTRY_H

#include "complextypeentry.h"

class SmartPointerTypeEntryPrivate;

class SmartPointerTypeEntry : public ComplexTypeEntry
{
public:
    using Instantiations = QList<const TypeEntry *>;

    explicit SmartPointerTypeEntry(const QString &entryName,
                                   const QString &getterName,
                                   TypeSystem::SmartPointerType type,
                                   const QString &refCountMethodName,
                                   const QVersionNumber &vr,
                                   const TypeEntry *parent);

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

    Instantiations instantiations() const;
    void setInstantiations(const Instantiations &i);
    bool matchesInstantiation(const TypeEntry *e) const;

    static QString getTargetFullName(const AbstractMetaType &metaType,
                                     bool includePackageName = true);
    static QString getTargetName(const AbstractMetaType &metaType);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    SmartPointerTypeEntry(SmartPointerTypeEntryPrivate *d);
};

#endif // SMARTPOINTERTYPEENTRY_H
