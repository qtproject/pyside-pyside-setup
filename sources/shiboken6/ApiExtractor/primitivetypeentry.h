// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PRIMITIVETYPEENTRY_H
#define PRIMITIVETYPEENTRY_H

#include "typesystem.h"
#include "customconversion_typedefs.h"

class PrimitiveTypeEntryPrivate;

/// A PrimitiveTypeEntry is user-defined type with conversion rules, a C++
/// primitive type for which a PrimitiveTypeConverter exists in libshiboken
/// or a typedef to a C++ primitive type as determined by AbstractMetaBuilder.
class PrimitiveTypeEntry : public TypeEntry
{
public:
    explicit PrimitiveTypeEntry(const QString &entryName, const QVersionNumber &vr,
                                const TypeEntryCPtr &parent);

    QString defaultConstructor() const;
    void setDefaultConstructor(const QString& defaultConstructor);
    bool hasDefaultConstructor() const;

    /**
     *   The PrimitiveTypeEntry pointed by this type entry if it
     *   represents a typedef).
     *   \return the type referenced by the typedef, or a null pointer
     *   if the current object is not an typedef
     */
    PrimitiveTypeEntryPtr referencedTypeEntry() const;

    /**
     *   Defines type referenced by this entry.
     *   \param referencedTypeEntry type referenced by this entry
     */
    void setReferencedTypeEntry(PrimitiveTypeEntryPtr referencedTypeEntry);

    /// Returns whether this entry references another entry.
    bool referencesType() const;

    bool preferredTargetLangType() const;
    void setPreferredTargetLangType(bool b);

    bool hasCustomConversion() const;
    void setCustomConversion(const CustomConversionPtr &customConversion);
    CustomConversionPtr customConversion() const;

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

protected:
    explicit PrimitiveTypeEntry(PrimitiveTypeEntryPrivate *d);
};

/// Finds the most basic primitive type that the typedef represents,
/// i.e. a type that is not an typedef'ed.
/// \return the most basic non-typedef'ed primitive type represented
/// by this typedef or self in case it is not a reference.
PrimitiveTypeEntryCPtr basicReferencedTypeEntry(const PrimitiveTypeEntryCPtr &e);
PrimitiveTypeEntryCPtr basicReferencedTypeEntry(const TypeEntryCPtr &e);

/// Finds the basic primitive type that the typedef represents
/// and was explicitly specified in the type system.
/// \return the basic primitive type that was explicitly specified in
/// the type system.
PrimitiveTypeEntryCPtr basicReferencedNonBuiltinTypeEntry(const PrimitiveTypeEntryCPtr &e);

#endif // PRIMITIVETYPEENTRY_H
