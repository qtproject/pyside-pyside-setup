/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef NAMESPACETYPEENTRY_H
#define NAMESPACETYPEENTRY_H

#include "complextypeentry.h"

class NamespaceTypeEntryPrivate;

class NamespaceTypeEntry : public ComplexTypeEntry
{
public:
    explicit NamespaceTypeEntry(const QString &entryName, const QVersionNumber &vr,
                                const TypeEntry *parent);

    TypeEntry *clone() const override;

    const NamespaceTypeEntry *extends() const;
    void setExtends(const NamespaceTypeEntry *e);

    const QRegularExpression &filePattern() const; // restrict files
    void setFilePattern(const QRegularExpression &r);

    bool hasPattern() const;

    bool matchesFile(const QString &needle) const;

    bool isVisible() const;
    void setVisibility(TypeSystem::Visibility v);

    // C++ 11 inline namespace, from code model
    bool isInlineNamespace() const;
    void setInlineNamespace(bool i);

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
