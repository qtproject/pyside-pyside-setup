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

#ifndef SMARTPOINTERTYPEENTRY_H
#define SMARTPOINTERTYPEENTRY_H

#include "complextypeentry.h"

class SmartPointerTypeEntryPrivate;

class SmartPointerTypeEntry : public ComplexTypeEntry
{
public:
    using Instantiations = QList<const TypeEntry *>;

    explicit SmartPointerTypeEntry(const QString &entryName,
                                   const QString &getterName,
                                   TypeSystem::SmartPointerType type,
                                   const QString &refCountMethodName,
                                   const QVersionNumber &vr,
                                   const TypeEntry *parent);

    TypeSystem::SmartPointerType smartPointerType() const;

    QString getter() const;

    QString refCountMethodName() const;

    QString valueCheckMethod() const;
    void setValueCheckMethod(const QString &);
    QString nullCheckMethod() const;
    void setNullCheckMethod(const QString &);
    QString resetMethod() const;
    void setResetMethod(const QString &);

    TypeEntry *clone() const override;

    Instantiations instantiations() const;
    void setInstantiations(const Instantiations &i);
    bool matchesInstantiation(const TypeEntry *e) const;

    static QString getTargetFullName(const AbstractMetaType &metaType,
                                     bool includePackageName = true);
    static QString getTargetName(const AbstractMetaType &metaType);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif
protected:
    SmartPointerTypeEntry(SmartPointerTypeEntryPrivate *d);
};

#endif // SMARTPOINTERTYPEENTRY_H
