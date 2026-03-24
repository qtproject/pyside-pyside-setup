// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODEMODEL_ENUMS_H
#define CODEMODEL_ENUMS_H

#include <QtCore/qflags.h>

enum ReferenceType : std::uint8_t {
    NoReference,
    LValueReference,
    RValueReference
};

enum EnumKind : std::uint8_t {
    CEnum,         // Standard C: enum Foo { value1, value2 }
    AnonymousEnum, //             enum { value1, value2 }
    EnumClass      // C++ 11    : enum class Foo { value1, value2 }
};

enum class Indirection : std::uint8_t
{
    Pointer, // int *
    ConstPointer // int *const
};

enum class ExceptionSpecification : std::uint8_t
{
    Unknown,
    NoExcept,
    Throws
};

enum class NamespaceType : std::uint8_t
{
    Default,
    Anonymous,
    Inline
};

enum class Access : std::uint8_t
{
    Private,
    Protected,
    Public
};

enum class FunctionAttribute : std::uint8_t {
    Abstract   = 0x00000001,
    Static     = 0x00000002,
    Virtual    = 0x00000004,
    Override   = 0x00000008,
    Final      = 0x00000010,
    Deprecated = 0x00000020, // Code annotation
    Explicit   = 0x00000040, // Constructor
    Defaulted  = 0x00000080
};

Q_DECLARE_FLAGS(FunctionAttributes, FunctionAttribute)
Q_DECLARE_OPERATORS_FOR_FLAGS(FunctionAttributes)

// C++ type category for TypeInfo, roughly reflecting clang's CXTypeKind
enum class TypeCategory : unsigned char {
    Other,
    Builtin,
    Enum,
    Pointer,
    Function,
    FunctionPointer, // not present in clang
    Void
};

#endif // CODEMODEL_ENUMS_H
