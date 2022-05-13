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

#ifndef CUSTOMCONVERSION_H
#define CUSTOMCONVERSION_H

#include "typesystem_enums.h"

#include <QtCore/QList>
#include <QtCore/QString>

class TypeEntry;

class CustomConversion
{
public:
    CustomConversion(TypeEntry* ownerType);
    ~CustomConversion();

    const TypeEntry* ownerType() const;
    QString nativeToTargetConversion() const;
    void setNativeToTargetConversion(const QString& nativeToTargetConversion);

    class TargetToNativeConversion
    {
    public:
        TargetToNativeConversion(const QString& sourceTypeName,
                                 const QString& sourceTypeCheck,
                                 const QString& conversion = QString());
        ~TargetToNativeConversion();

        const TypeEntry* sourceType() const;
        void setSourceType(const TypeEntry* sourceType);
        bool isCustomType() const;
        QString sourceTypeName() const;
        QString sourceTypeCheck() const;
        QString conversion() const;
        void setConversion(const QString& conversion);
    private:
        struct TargetToNativeConversionPrivate;
        TargetToNativeConversionPrivate* m_d;
    };

    /**
     *  Returns true if the target to C++ custom conversions should
     *  replace the original existing ones, and false if the custom
     *  conversions should be added to the original.
     */
    bool replaceOriginalTargetToNativeConversions() const;
    void setReplaceOriginalTargetToNativeConversions(bool replaceOriginalTargetToNativeConversions);

    using TargetToNativeConversions = QList<TargetToNativeConversion *>;
    bool hasTargetToNativeConversions() const;
    TargetToNativeConversions& targetToNativeConversions();
    const TargetToNativeConversions& targetToNativeConversions() const;
    void addTargetToNativeConversion(const QString& sourceTypeName,
                                     const QString& sourceTypeCheck,
                                     const QString& conversion = QString());
private:
    struct CustomConversionPrivate;
    CustomConversionPrivate* m_d;
};

#endif // CUSTOMCONVERSION_H
