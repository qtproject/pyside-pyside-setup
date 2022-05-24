// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_ENUMS_H
#define ABSTRACTMETALANG_ENUMS_H

#include <QtCore/QFlags>

enum class FunctionQueryOption {
    AnyConstructor               = 0x0000001, // Any constructor (copy/move)
    Constructors                 = 0x0000002, // Constructors except copy/move
    CopyConstructor              = 0x0000004, // Only copy constructors
    //Destructors                  = 0x0000002, // Only destructors. Not included in class.
    FinalInTargetLangFunctions   = 0x0000008, // Only functions that are non-virtual in TargetLang
    ClassImplements              = 0x0000020, // Only functions implemented by the current class
    StaticFunctions              = 0x0000080, // Only static functions
    Signals                      = 0x0000100, // Only signals
    NormalFunctions              = 0x0000200, // Only functions that aren't signals
    Visible                      = 0x0000400, // Only public and protected functions
    WasPublic                    = 0x0001000, // Only functions that were originally public
    NonStaticFunctions           = 0x0004000, // No static functions
    Empty                        = 0x0008000, // Empty overrides of abstract functions
    Invisible                    = 0x0010000, // Only private functions
    VirtualInCppFunctions        = 0x0020000, // Only functions that are virtual in C++
    VirtualInTargetLangFunctions = 0x0080000, // Only functions which are virtual in TargetLang
    NotRemoved                   = 0x0400000, // Only functions that have not been removed
    OperatorOverloads            = 0x2000000, // Only functions that are operator overloads
    GenerateExceptionHandling    = 0x4000000,
    GetAttroFunction             = 0x8000000,
    SetAttroFunction            = 0x10000000
};

Q_DECLARE_FLAGS(FunctionQueryOptions, FunctionQueryOption)
Q_DECLARE_OPERATORS_FOR_FLAGS(FunctionQueryOptions)

enum class OperatorQueryOption {
    ArithmeticOp            = 0x01, // Arithmetic: +, -, *, /, %, +=, -=, *=, /=, %=, unary+, unary-
    IncDecrementOp          = 0x02, // ++, --
    BitwiseOp               = 0x04, // Bitwise: <<, <<=, >>, >>=, ~, &, &=, |, |=, ^, ^=
    ComparisonOp            = 0x08, // Comparison: <, <=, >, >=, !=, ==
    // Comparing to instances of owner class: <, <=, >, >=, !=, ==
    // (bool operator==(QByteArray,QByteArray) but not bool operator==(QByteArray,const char *)
    SymmetricalComparisonOp = 0x10,
    LogicalOp               = 0x20, // Logical: !, &&, ||
    ConversionOp            = 0x40, // Conversion: operator [const] TYPE()
    SubscriptionOp          = 0x80, // Subscription: []
    AssignmentOp            = 0x100  // Assignment: =
};

Q_DECLARE_FLAGS(OperatorQueryOptions, OperatorQueryOption)
Q_DECLARE_OPERATORS_FOR_FLAGS(OperatorQueryOptions)

#endif // ABSTRACTMETALANG_ENUMS_H
