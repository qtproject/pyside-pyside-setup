// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VALUETYPEENTRY_H
#define VALUETYPEENTRY_H

#include "complextypeentry.h"
#include "customconversion_typedefs.h"

class ValueTypeEntry : public ComplexTypeEntry
{
public:
    explicit ValueTypeEntry(const QString &entryName, const QVersionNumber &vr,
                            const TypeEntryCPtr &parent);

    bool hasCustomConversion() const;
    void setCustomConversion(const CustomConversionPtr &customConversion);
    CustomConversionPtr customConversion() const;

    // FIXME PYSIDE7: Remove
    /// Set the target type conversion rule
    void setTargetConversionRule(const QString &conversionRule);

    /// Returns the target type conversion rule
    QString targetConversionRule() const;

    /// TODO-CONVERTER: mark as deprecated
    bool hasTargetConversionRule() const;

    bool isValue() const override;

    TypeEntry *clone() const override;

protected:
    explicit ValueTypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                            const TypeEntryCPtr &parent);
    explicit ValueTypeEntry(ComplexTypeEntryPrivate *d);
};

#endif // VALUETYPEENTRY_H
