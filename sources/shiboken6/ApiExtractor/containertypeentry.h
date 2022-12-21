// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONTAINERTYPEENTRY_H
#define CONTAINERTYPEENTRY_H

#include "complextypeentry.h"
#include "customconversion_typedefs.h"

class ContainerTypeEntryPrivate;

struct OpaqueContainer // Generate an opaque container for an instantiation under name
{
    QStringList instantiations;
    QString name;

    QString templateParameters() const;
};

using OpaqueContainers = QList<OpaqueContainer>;

class ContainerTypeEntry : public ComplexTypeEntry
{
public:

    enum ContainerKind {
        ListContainer,
        SetContainer,
        MapContainer,
        MultiMapContainer,
        PairContainer,
        SpanContainer, // Fixed size
    };

    explicit ContainerTypeEntry(const QString &entryName, ContainerKind containerKind,
                                const QVersionNumber &vr, const TypeEntryCPtr &parent);

    ContainerKind containerKind() const;

    /// Number of template parameters (except allocators)
    qsizetype templateParameterCount() const;

    const OpaqueContainers &opaqueContainers() const;
    void appendOpaqueContainers(const OpaqueContainers &l);
    bool generateOpaqueContainer(const QStringList &instantiations) const;
    QString opaqueContainerName(const QStringList &instantiations) const;

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

QDebug operator<<(QDebug d, const OpaqueContainer &oc);

#endif // CONTAINERTYPEENTRY_H
