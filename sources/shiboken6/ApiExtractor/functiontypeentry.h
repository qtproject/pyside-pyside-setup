// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FUNCTIONTYPEENTRY_H
#define FUNCTIONTYPEENTRY_H

#include "typesystem.h"
#include "typesystem_enums.h"

class FunctionTypeEntryPrivate;

class FunctionTypeEntry : public TypeEntry
{
public:
    explicit FunctionTypeEntry(const QString& name, const QString& signature,
                               const QVersionNumber &vr,
                               const TypeEntryCPtr &parent);

    const QStringList &signatures() const;
    bool hasSignature(const QString& signature) const;
    void addSignature(const QString& signature);

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase sc);

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

protected:
    explicit FunctionTypeEntry(FunctionTypeEntryPrivate *d);
};

#endif // FUNCTIONTYPEENTRY_H
