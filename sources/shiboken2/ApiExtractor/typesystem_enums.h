/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef TYPESYSTEM_ENUMS_H
#define TYPESYSTEM_ENUMS_H

namespace TypeSystem
{
enum Language {
    NoLanguage          = 0x0000,
    TargetLangCode      = 0x0001,
    NativeCode          = 0x0002,
    ShellCode           = 0x0004,

    // masks
    All                 = TargetLangCode | NativeCode | ShellCode,

    TargetLangAndNativeCode   = TargetLangCode | NativeCode
};

enum class AllowThread {
    Allow,
    Disallow,
    Auto,
    Unspecified
};

enum Ownership {
    InvalidOwnership,
    DefaultOwnership,
    TargetLangOwnership,
    CppOwnership
};

enum CodeSnipPosition {
    CodeSnipPositionBeginning,
    CodeSnipPositionEnd,
    CodeSnipPositionDeclaration,
    CodeSnipPositionAny,
    CodeSnipPositionInvalid
};

enum DocModificationMode {
    DocModificationAppend,
    DocModificationPrepend,
    DocModificationReplace,
    DocModificationXPathReplace,
    DocModificationInvalid
};

enum class ExceptionHandling {
    Unspecified,
    Off,
    AutoDefaultToOff,
    AutoDefaultToOn,
    On
};

enum Visibility { // For namespaces
    Unspecified,
    Visible,
    Invisible,
    Auto
};

enum : int { OverloadNumberUnset = -1, OverloadNumberDefault = 99999 };

} // namespace TypeSystem

#endif // TYPESYSTEM_ENUMS_H
