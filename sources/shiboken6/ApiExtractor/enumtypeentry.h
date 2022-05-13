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

#ifndef ENUMTYPEENTRY_H
#define ENUMTYPEENTRY_H

#include "typesystem.h"

class EnumTypeEntryPrivate;
class EnumValueTypeEntry;
class FlagsTypeEntry;

class EnumTypeEntry : public TypeEntry
{
public:
    explicit EnumTypeEntry(const QString &entryName,
                           const QVersionNumber &vr,
                           const TypeEntry *parent);

    QString targetLangQualifier() const;

    QString qualifier() const;

    const EnumValueTypeEntry *nullValue() const;
    void setNullValue(const EnumValueTypeEntry *n);

    void setFlags(FlagsTypeEntry *flags);
    FlagsTypeEntry *flags() const;

    bool isEnumValueRejected(const QString &name) const;
    void addEnumValueRejection(const QString &name);
    QStringList enumValueRejections() const;

    TypeEntry *clone() const override;
#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    explicit EnumTypeEntry(EnumTypeEntryPrivate *d);
};

#endif // ENUMTYPEENTRY_H
