// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CUSTOMCONVERSION_H
#define CUSTOMCONVERSION_H

#include "customconversion_typedefs.h"
#include "typesystem_typedefs.h"

#include <QtCore/QList>
#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QDebug)

class TypeEntry;

class TargetToNativeConversion
{
public:
    explicit TargetToNativeConversion(const QString &sourceTypeName,
                                      const QString &sourceTypeCheck,
                                      const QString &conversion = {});

    TypeEntryCPtr sourceType() const;
    void setSourceType(const TypeEntryCPtr &sourceType);
    bool isCustomType() const;
    QString sourceTypeName() const;
    QString sourceTypeCheck() const;
    QString conversion() const;
    void setConversion(const QString &conversion);

    void formatDebug(QDebug &d) const;

private:
    TypeEntryCPtr m_sourceType;
    QString m_sourceTypeName;
    QString m_sourceTypeCheck;
    QString m_conversion;
};

using TargetToNativeConversions = QList<TargetToNativeConversion>;

class CustomConversion
{
public:
    explicit CustomConversion(const TypeEntryCPtr &ownerType);

    TypeEntryCPtr ownerType() const;
    QString nativeToTargetConversion() const;
    void setNativeToTargetConversion(const QString &nativeToTargetConversion);

    /// Returns true if the target to C++ custom conversions should
    /// replace the original existing ones, and false if the custom
    /// conversions should be added to the original.
    bool replaceOriginalTargetToNativeConversions() const;
    void setReplaceOriginalTargetToNativeConversions(bool r);

    bool hasTargetToNativeConversions() const;
    TargetToNativeConversions &targetToNativeConversions();
    const TargetToNativeConversions &targetToNativeConversions() const;
    void addTargetToNativeConversion(const QString &sourceTypeName,
                                     const QString &sourceTypeCheck,
                                     const QString &conversion = QString());

    /// Return the custom conversion of a type; helper for type system parser
    static CustomConversionPtr getCustomConversion(const TypeEntryCPtr &type);

    void formatDebug(QDebug &debug) const;

private:
    TypeEntryCPtr m_ownerType;
    QString m_nativeToTargetConversion;
    TargetToNativeConversions m_targetToNativeConversions;
    bool m_replaceOriginalTargetToNativeConversions = false;
};

QDebug operator<<(QDebug debug, const TargetToNativeConversion &t);
QDebug operator<<(QDebug debug, const CustomConversion &c);
QDebug operator<<(QDebug debug, const CustomConversionPtr &cptr);

#endif // CUSTOMCONVERSION_H
