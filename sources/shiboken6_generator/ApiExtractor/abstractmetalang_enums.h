// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef ABSTRACTMETALANG_ENUMS_H
#define ABSTRACTMETALANG_ENUMS_H

#include <QtCore/qflags.h>

enum class ComparisonOperatorType : std::uint8_t {
    OperatorEqual        = 0x01,
    OperatorNotEqual     = 0x02,
    EqualityMask         = OperatorEqual | OperatorNotEqual,
    OperatorLess         = 0x04,
    OperatorLessEqual    = 0x08,
    OperatorGreater      = 0x10,
    OperatorGreaterEqual = 0x20,
    OrderingMask         = OperatorLess | OperatorLessEqual | OperatorGreater | OperatorGreaterEqual,
    AllMask              = EqualityMask | OrderingMask
};

Q_DECLARE_FLAGS(ComparisonOperators, ComparisonOperatorType)
Q_DECLARE_OPERATORS_FOR_FLAGS(ComparisonOperators)

enum class FunctionQueryOption : std::uint32_t {
    AnyConstructor               = 0x0000001, // Any constructor (copy/move)
    Constructors                 = 0x0000002, // Constructors except copy/move
    DefaultConstructor           = 0x0000004, // Only Default constructors
    CopyConstructor              = 0x0000008, // Only copy constructors
    MoveConstructor              = 0x0000010, // Only move constructors
    AssignmentOperator           = 0x0000020, // Only assignment operator
    MoveAssignmentOperator       = 0x0000040, // Only move assignment operator
    ClassImplements              = 0x0000080, // Only functions implemented by the current class
    StaticFunctions              = 0x0000100, // Only static functions
    Signals                      = 0x0000200, // Only signals
    NormalFunctions              = 0x0000400, // Only functions that aren't signals
    Visible                      = 0x0000800, // Only public and protected functions
    NonStaticFunctions           = 0x0004000, // No static functions
    Empty                        = 0x0008000, // Empty overrides of abstract functions
    Invisible                    = 0x0010000, // Only private functions
    VirtualInCppFunctions        = 0x0020000, // Only functions that are virtual in C++
    NotRemoved                   = 0x0400000, // Only functions that have not been removed
    OperatorOverloads            = 0x2000000, // Only functions that are operator overloads
    GenerateExceptionHandling    = 0x4000000,
    GetAttroFunction             = 0x8000000,
    SetAttroFunction            = 0x10000000
};

Q_DECLARE_FLAGS(FunctionQueryOptions, FunctionQueryOption)
Q_DECLARE_OPERATORS_FOR_FLAGS(FunctionQueryOptions)

enum class OperatorQueryOption : std::uint16_t {
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

// Internal flags of AbstractMetaFunction not relevant for comparing functions
enum class InternalFunctionFlag : std::uint16_t
{
    // Binary operator whose leading/trailing argument was removed by metabuilder
    OperatorLeadingClassArgumentRemoved  = 0x001,
    OperatorTrailingClassArgumentRemoved = 0x002,
    OperatorClassArgumentByValue = 0x004, // The removed class argument was passed by value
    OperatorCpp20Spaceship       = 0x008, // Synthesized from operator<=> in C++ 20
    OperatorCpp20NonEquality     = 0x010, // Synthesized from operator== in C++ 20
    OperatorMask                 = 0x01F,
    InheritedFromTemplate        = 0x020, // Inherited from a template in metabuilder
    HiddenFriend                 = 0x040,
    PrivateSignal                = 0x080, // Private Qt signal (cannot emit from client code)
    CovariantReturn              = 0x100, // Return type of virtual function differs (eg clone())
};

Q_DECLARE_FLAGS(InternalFunctionFlags, InternalFunctionFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(InternalFunctionFlags)

#endif // ABSTRACTMETALANG_ENUMS_H
