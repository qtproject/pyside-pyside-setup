// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_ENUMS_H
#define TYPESYSTEM_ENUMS_H

namespace TypeSystem
{
enum Language {
    TargetLangCode      = 0x0001,
    NativeCode          = 0x0002,
    ShellCode           = 0x0004,

    // masks
    All                 = TargetLangCode | NativeCode | ShellCode,

    TargetLangAndNativeCode   = TargetLangCode | NativeCode
};

enum class AllowThread {
    Unspecified,
    Allow,
    Disallow,
    Auto
};

enum Ownership {
    UnspecifiedOwnership,
    DefaultOwnership,
    TargetLangOwnership,
    CppOwnership
};

enum CodeSnipPosition {
    CodeSnipPositionBeginning,
    CodeSnipPositionEnd,
    CodeSnipPositionDeclaration,
    CodeSnipPositionAny
};

enum DocModificationMode {
    DocModificationAppend,
    DocModificationPrepend,
    DocModificationReplace,
    DocModificationXPathReplace
};

enum class ExceptionHandling {
    Unspecified,
    Off,
    AutoDefaultToOff,
    AutoDefaultToOn,
    On
};

enum class SnakeCase {
    Unspecified,
    Disabled,
    Enabled,
    Both
};

enum Visibility { // For namespaces
    Unspecified,
    Visible,
    Invisible,
    Auto
};

enum class BoolCast { // Generate nb_bool (overriding command line)
    Unspecified,
    Disabled,
    Enabled
};

enum class CPythonType
{
    Bool,
    Float,
    Integer,
    String,
    Other
};

enum class QtMetaTypeRegistration
{
    Unspecified,
    Enabled,
    BaseEnabled, // Registration only for the base class of a hierarchy
    Disabled
};

enum class SmartPointerType {
    Shared,
    Unique,
    Handle,
    ValueHandle
};

enum class PythonEnumType {
    Unspecified,
    Enum,
    IntEnum,
    Flag,
    IntFlag
};

enum : int { OverloadNumberUnset = -1, OverloadNumberDefault = 99999 };

} // namespace TypeSystem

#endif // TYPESYSTEM_ENUMS_H
