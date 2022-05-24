// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODEMODEL_ENUMS_H
#define CODEMODEL_ENUMS_H

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

#endif // CODEMODEL_ENUMS_H
