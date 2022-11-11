// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NAMESPACETYPEENTRY_H
#define NAMESPACETYPEENTRY_H

#include "complextypeentry.h"

class NamespaceTypeEntryPrivate;

class NamespaceTypeEntry : public ComplexTypeEntry
{
public:
    explicit NamespaceTypeEntry(const QString &entryName, const QVersionNumber &vr,
                                const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

    NamespaceTypeEntryCPtr extends() const;
    void setExtends(const NamespaceTypeEntryCPtr &e);

    const QRegularExpression &filePattern() const; // restrict files
    void setFilePattern(const QRegularExpression &r);

    bool hasPattern() const;

    bool matchesFile(const QString &needle) const;

    bool isVisible() const;
    void setVisibility(TypeSystem::Visibility v);

    // C++ 11 inline namespace, from code model
    bool isInlineNamespace() const;
    void setInlineNamespace(bool i);

    static bool isVisibleScope(const TypeEntryCPtr &e);
    static bool isVisibleScope(const TypeEntry *e);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

     // Whether to generate "using namespace" into wrapper
    bool generateUsing() const;
    void setGenerateUsing(bool generateUsing);

protected:
    explicit NamespaceTypeEntry(NamespaceTypeEntryPrivate *d);
};

#endif // NAMESPACETYPEENTRY_H
