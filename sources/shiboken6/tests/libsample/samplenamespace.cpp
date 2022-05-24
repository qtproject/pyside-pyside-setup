// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include <cstdlib>
#include <time.h>
#include "samplenamespace.h"

using namespace std;

namespace SampleNamespace
{

// PYSIDE-817, scoped enums must not be converted to int in the wrappers generated
// for the protected hacks
SomeClass::PublicScopedEnum SomeClass::protectedMethodReturningPublicScopedEnum() const
{
    return PublicScopedEnum::v1;
}

OutValue
enumInEnumOut(InValue in)
{
    OutValue retval;
    switch(in) {
        case ZeroIn:
            retval = ZeroOut;
            break;
        case OneIn:
            retval = OneOut;
            break;
        case TwoIn:
            retval = TwoOut;
            break;
        default:
            retval = (OutValue) -1;
    }
    return retval;
}

Option
enumArgumentWithDefaultValue(Option opt)
{
    return opt;
}

int
getNumber(Option opt)
{
    int retval;
    switch(opt) {
        case RandomNumber:
            retval = rand() % 100;
            break;
        case UnixTime:
            retval = (int) time(nullptr);
            break;
        default:
            retval = 0;
    }
    return retval;
}

void
doSomethingWithArray(const unsigned char* data, unsigned int size, const char* format)
{
    // This function does nothing in fact.
    // It is here as a dummy copy of QPixmap.loadFromData method
    // to check compilation issues, i.e. if it compiles, it's ok.
}

int
enumItemAsDefaultValueToIntArgument(int value)
{
    return value;
}

void
forceDecisorSideA(ObjectType* object)
{
}

void
forceDecisorSideA(const Point& pt, const Str& text, ObjectType* object)
{
}

void
forceDecisorSideB(int a, ObjectType* object)
{
}

void
forceDecisorSideB(int a, const Point& pt, const Str& text, ObjectType* object)
{
}

double
passReferenceToValueType(const Point& point, double multiplier)
{
    return (point.x() + point.y()) * multiplier;
}

int
passReferenceToObjectType(const ObjectType& obj, int multiplier)
{
    return obj.objectName().size() * multiplier;
}

int variableInNamespace = 42;

} // namespace SampleNamespace
