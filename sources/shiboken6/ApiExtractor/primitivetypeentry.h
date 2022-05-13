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

#ifndef PRIMITIVETYPEENTRY_H
#define PRIMITIVETYPEENTRY_H

#include "typesystem.h"

class PrimitiveTypeEntryPrivate;

/// A PrimitiveTypeEntry is user-defined type with conversion rules, a C++
/// primitive type for which a PrimitiveTypeConverter exists in libshiboken
/// or a typedef to a C++ primitive type as determined by AbstractMetaBuilder.
class PrimitiveTypeEntry : public TypeEntry
{
public:
    explicit PrimitiveTypeEntry(const QString &entryName, const QVersionNumber &vr,
                                const TypeEntry *parent);

    QString defaultConstructor() const;
    void setDefaultConstructor(const QString& defaultConstructor);
    bool hasDefaultConstructor() const;

    /**
     *   The PrimitiveTypeEntry pointed by this type entry if it
     *   represents a typedef).
     *   \return the type referenced by the typedef, or a null pointer
     *   if the current object is not an typedef
     */
    PrimitiveTypeEntry *referencedTypeEntry() const;

    /**
     *   Defines type referenced by this entry.
     *   \param referencedTypeEntry type referenced by this entry
     */
    void setReferencedTypeEntry(PrimitiveTypeEntry* referencedTypeEntry);

    /// Finds the most basic primitive type that the typedef represents,
    /// i.e. a type that is not an typedef'ed.
    /// \return the most basic non-typedef'ed primitive type represented
    /// by this typedef or self in case it is not a reference.
    const PrimitiveTypeEntry* basicReferencedTypeEntry() const;

    /// Finds the basic primitive type that the typedef represents
    /// and was explicitly specified in the type system.
    /// \return the basic primitive type that was explicitly specified in
    /// the type system.
    const PrimitiveTypeEntry* basicReferencedNonBuiltinTypeEntry() const;

    /// Returns whether this entry references another entry.
    bool referencesType() const;

    bool preferredTargetLangType() const;
    void setPreferredTargetLangType(bool b);

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

protected:
    explicit PrimitiveTypeEntry(PrimitiveTypeEntryPrivate *d);
};

#endif // PRIMITIVETYPEENTRY_H
