// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEDEFENTRY_H
#define TYPEDEFENTRY_H

#include "complextypeentry.h"

class TypedefEntryPrivate;

class TypedefEntry : public ComplexTypeEntry
{
public:
    explicit TypedefEntry(const QString &entryName,
                          const QString &sourceType,
                          const QVersionNumber &vr,
                          const TypeEntry *parent);

    QString sourceType() const;
    void setSourceType(const QString &s);

    TypeEntry *clone() const override;

    const ComplexTypeEntry *source() const;
    void setSource(const ComplexTypeEntry *source);

    ComplexTypeEntry *target() const;
    void setTarget(ComplexTypeEntry *target);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    explicit TypedefEntry(TypedefEntryPrivate *d);
};

#endif // TYPEDEFENTRY_H
