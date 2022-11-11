// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TEMPLATEARGUMENTENTRY_H
#define TEMPLATEARGUMENTENTRY_H

#include "typesystem.h"

class TemplateArgumentEntryPrivate;

class TemplateArgumentEntry : public TypeEntry
{
public:
    explicit TemplateArgumentEntry(const QString &entryName, const QVersionNumber &vr,
                                   const TypeEntryCPtr &parent);

    int ordinal() const;
    void setOrdinal(int o);

    TypeEntry *clone() const override;

protected:
    explicit TemplateArgumentEntry(TemplateArgumentEntryPrivate *d);
};

#endif // TEMPLATEARGUMENTENTRY_H
