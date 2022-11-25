// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONFIGURABLETYPEENTRY_H
#define CONFIGURABLETYPEENTRY_H

#include "typesystem.h"

class ConfigurableTypeEntryPrivate;

class ConfigurableTypeEntry : public TypeEntry
{
public:
    explicit ConfigurableTypeEntry(const QString &entryName, Type t,
                                   const QVersionNumber &vr,
                                   const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

    QString configCondition() const;
    void setConfigCondition(const QString &c);
    bool hasConfigCondition() const;

protected:
    explicit ConfigurableTypeEntry(ConfigurableTypeEntryPrivate *d);
};

#endif // CONFIGURABLETYPEENTRY_H
