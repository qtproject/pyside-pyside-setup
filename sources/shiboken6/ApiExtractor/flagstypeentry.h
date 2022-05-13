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

#ifndef FLAGSTYPEENTRY_H
#define FLAGSTYPEENTRY_H

#include "typesystem.h"

class EnumTypeEntry;
class FlagsTypeEntryPrivate;

class FlagsTypeEntry : public TypeEntry
{
public:
    explicit FlagsTypeEntry(const QString &entryName, const QVersionNumber &vr,
                            const TypeEntry *parent);

    QString originalName() const;
    void setOriginalName(const QString &s);

    QString flagsName() const;
    void setFlagsName(const QString &name);

    EnumTypeEntry *originator() const;
    void setOriginator(EnumTypeEntry *e);

    TypeEntry *clone() const override;

protected:
    explicit FlagsTypeEntry(FlagsTypeEntryPrivate *d);

    QString buildTargetLangName() const override;
};

#endif // FLAGSTYPEENTRY_H
