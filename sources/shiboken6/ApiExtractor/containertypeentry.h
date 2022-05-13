/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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

#ifndef CONTAINERTYPEENTRY_H
#define CONTAINERTYPEENTRY_H

#include "complextypeentry.h"

class ContainerTypeEntryPrivate;

class ContainerTypeEntry : public ComplexTypeEntry
{
public:
    struct OpaqueContainer // Generate an opaque container for an instantiation under name
    {
        QString instantiation;
        QString name;
    };
    using OpaqueContainers = QList<OpaqueContainer>;

    enum ContainerKind {
        ListContainer,
        SetContainer,
        MapContainer,
        MultiMapContainer,
        PairContainer,
    };

    explicit ContainerTypeEntry(const QString &entryName, ContainerKind containerKind,
                                const QVersionNumber &vr, const TypeEntry *parent);

    ContainerKind containerKind() const;

    const OpaqueContainers &opaqueContainers() const;
    void addOpaqueContainer(OpaqueContainer r);
    bool generateOpaqueContainer(const QString &instantiation) const;
    QString opaqueContainerName(const QString &instantiation) const;

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    explicit ContainerTypeEntry(ContainerTypeEntryPrivate *d);
};

#endif // CONTAINERTYPEENTRY_H
