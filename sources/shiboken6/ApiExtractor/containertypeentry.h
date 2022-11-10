// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONTAINERTYPEENTRY_H
#define CONTAINERTYPEENTRY_H

#include "complextypeentry.h"
#include "customconversion_typedefs.h"

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

    bool hasCustomConversion() const;
    void setCustomConversion(const CustomConversionPtr &customConversion);
    CustomConversionPtr customConversion() const;

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    explicit ContainerTypeEntry(ContainerTypeEntryPrivate *d);
};

#endif // CONTAINERTYPEENTRY_H
