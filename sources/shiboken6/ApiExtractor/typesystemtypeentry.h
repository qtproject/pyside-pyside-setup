// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEMTYPEENTRY_H
#define TYPESYSTEMTYPEENTRY_H

#include "typesystem.h"
#include "typesystem_enums.h"
#include "typesystem_typedefs.h"

class TypeSystemTypeEntry : public TypeEntry
{
public:
    explicit TypeSystemTypeEntry(const QString &entryName, const QVersionNumber &vr,
                                 const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase sc);

    const CodeSnipList &codeSnips() const;
    CodeSnipList &codeSnips();
    void addCodeSnip(const CodeSnip &codeSnip);

protected:
    explicit TypeSystemTypeEntry(TypeEntryPrivate *d);
};

#endif // TYPESYSTEMTYPEENTRY_H
