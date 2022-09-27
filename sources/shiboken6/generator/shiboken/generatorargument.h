// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GENERATORARGUMENT_H
#define GENERATORARGUMENT_H

#include <QtCore/QFlags>
#include <QtCore/qobjectdefs.h>

QT_FORWARD_DECLARE_CLASS(QDebug)

class AbstractMetaType;

/// A struct containing information on how the generator processes a function argument.
struct GeneratorArgument
{
    Q_GADGET

public:
    enum class Type {
        Other,
        Primitive,
        Enum,
        Flags,
        Container,
        CppPrimitiveArray
    };
    Q_ENUM(Type)

    enum class Conversion {
        Default,
        CppPrimitiveArray, // Similar to Default except default values
        Pointer,
        ValueOrPointer
    };
    Q_ENUM(Conversion)

    enum class Flag {
        TreatAsPointer = 0x1,
        PointerOrObjectType = 0x2,
        MayHaveImplicitConversion = 0x4,
        ValueOrPointer = 0x8,
    };
    Q_ENUM(Flag)
    Q_DECLARE_FLAGS(Flags, Flag)

    static GeneratorArgument fromMetaType(const AbstractMetaType &type);

    Flags flags;
    /// Indirections from generated "cppArg<n>" variable to function argument.
    qsizetype indirections = 0;
    Type type = Type::Other;
    Conversion conversion = Conversion::Default;
};

Q_DECLARE_OPERATORS_FOR_FLAGS(GeneratorArgument::Flags)

QDebug operator<<(QDebug debug, const GeneratorArgument &a);

#endif // GENERATORARGUMENT_H
