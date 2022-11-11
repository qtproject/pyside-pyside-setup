// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "generatorargument.h"
#include <abstractmetatype.h>
#include <messages.h>
#include <typesystem.h>

#include <QtCore/QDebug>
#include <QtCore/QSet>

static bool isCppPrimitiveString(const AbstractMetaType &type)
{
    return type.referenceType() == NoReference && type.indirections() == 1
        && AbstractMetaType::cppSignedCharTypes().contains(type.name());
}

GeneratorArgument GeneratorArgument::fromMetaType(const AbstractMetaType &type)
{
    GeneratorArgument result;

    const auto typeEntry = type.typeEntry();
    if (typeEntry->isCustom() || typeEntry->isVarargs())
        return result;

    result.indirections = -type.indirectionsV().size();
    if (isCppPrimitiveString(type)
        || type.isVoidPointer()
        || type.typeUsagePattern() == AbstractMetaType::NativePointerAsArrayPattern) {
        result.indirections += 1;
    }

    if (typeEntry->isEnum()) {
        result.type = Type::Enum;
    } else if (typeEntry->isFlags()) {
        result.type = Type::Flags;
    } else if (typeEntry->isContainer()) {
        result.type = Type::Container;
    } else {
        if (typeEntry->isPrimitive())
            result.type = Type::Primitive;

        const AbstractMetaTypeList &nestedArrayTypes = type.nestedArrayTypes();
        if (!nestedArrayTypes.isEmpty()) {
            if (nestedArrayTypes.constLast().isCppPrimitive()) {
                result.type = Type::CppPrimitiveArray;
            } else {
                static QSet<QString> warnedTypes;
                const QString &signature = type.cppSignature();
                if (!warnedTypes.contains(signature)) {
                    warnedTypes.insert(signature);
                    qWarning("%s", qPrintable(msgUnknownArrayPointerConversion(signature)));
                }
                result.indirections -= 1;
            }
        }
    }

    if (result.type == Type::Other || result.type == Type::Primitive) {
        if (type.valueTypeWithCopyConstructorOnlyPassed()) {
            result.flags.setFlag(Flag::TreatAsPointer);
        } else if ((type.isObjectType() || type.isPointer())
                   && !type.isUserPrimitive() && !type.isExtendedCppPrimitive()) {
            result.flags.setFlag(Flag::PointerOrObjectType);
        } else if (type.referenceType() == LValueReference
                   && !type.isUserPrimitive()
                   && !type.isExtendedCppPrimitive()) {
            result.flags.setFlag(Flag::MayHaveImplicitConversion);
        }
    }

    // For implicit conversions or containers, either value or pointer conversion
    // may occur. An implicit conversion uses value conversion whereas the object
    // itself uses pointer conversion. For containers, the PyList/container
    // conversion is by value whereas opaque containers use pointer conversion.
    // For a container passed by pointer, a local variable is also needed.
    if (result.flags.testFlag(Flag::MayHaveImplicitConversion)
        || type.generateOpaqueContainer()
        || (result.type == Type::Container && result.indirections != 0)) {
        result.flags.setFlag(Flag::ValueOrPointer);
    }

    if (result.type == Type::CppPrimitiveArray) {
        result.conversion = Conversion::CppPrimitiveArray;
    } else if (result.flags.testFlag(Flag::ValueOrPointer)) {
        result.conversion = Conversion::ValueOrPointer;
        ++result.indirections;
    } else if (result.flags.testAnyFlags(Flag::TreatAsPointer | Flag::PointerOrObjectType)) {
        result.conversion = Conversion::Pointer;
        ++result.indirections;
    }

    return result;
}

QDebug operator<<(QDebug debug, const GeneratorArgument &a)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "GeneratorArgument(" << a.type;
    if (a.conversion != GeneratorArgument::Conversion::Default)
        debug << ", conversion=" << a.conversion;
    if (a.flags)
        debug << ", flags(" << a.flags;
    if (a.indirections != 0)
        debug << ", indirections=" << a.indirections;
    debug << ')';
    return debug;
}
