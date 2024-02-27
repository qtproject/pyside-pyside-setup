// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODEMODEL_ENUMS_H
#define CODEMODEL_ENUMS_H

#include <QtCore/qflags.h>

enum ReferenceType {
    NoReference,
    LValueReference,
    RValueReference
};

enum EnumKind {
    CEnum,         // Standard C: enum Foo { value1, value2 }
    AnonymousEnum, //             enum { value1, value2 }
    EnumClass      // C++ 11    : enum class Foo { value1, value2 }
};

enum class Indirection
{
    Pointer, // int *
    ConstPointer // int *const
};

enum class ExceptionSpecification
{
    Unknown,
    NoExcept,
    Throws
};

enum class NamespaceType
{
    Default,
    Anonymous,
    Inline
};

enum class Access
{
    Private,
    Protected,
    Public
};

enum class FunctionAttribute {
    Abstract   = 0x00000001,
    Static     = 0x00000002,
    Virtual    = 0x00000004,
    Override   = 0x00000008,
    Final      = 0x00000010,
    Deprecated = 0x00000020, // Code annotation
    Explicit   = 0x00000040, // Constructor
};

Q_DECLARE_FLAGS(FunctionAttributes, FunctionAttribute)
Q_DECLARE_OPERATORS_FOR_FLAGS(FunctionAttributes)

#endif // CODEMODEL_ENUMS_H
