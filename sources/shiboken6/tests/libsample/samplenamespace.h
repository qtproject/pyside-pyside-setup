// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SAMPLENAMESPACE_H
#define SAMPLENAMESPACE_H

#include "libsamplemacros.h"
#include "str.h"
#include "point.h"
#include "objecttype.h"

#include <list>

// Anonymous global enum
enum {
    AnonymousGlobalEnum_Value0,
    AnonymousGlobalEnum_Value1
};

namespace SampleNamespace
{

inline namespace InlineNamespace
{
    enum EnumWithinInlineNamespace { EWIN_Value0, EWIN_Value1 };

    class LIBSAMPLE_API ClassWithinInlineNamespace {
    public:
        ClassWithinInlineNamespace() = default;
        ~ClassWithinInlineNamespace() = default;
        ClassWithinInlineNamespace(const ClassWithinInlineNamespace &) = default;
        ClassWithinInlineNamespace &operator=(const ClassWithinInlineNamespace &) = default;

        void setValue(EnumWithinInlineNamespace v) { m_value = v; }
        EnumWithinInlineNamespace value() const { return m_value; }

    private:
        EnumWithinInlineNamespace m_value = EWIN_Value0;
    };
} // inline ns

enum Option {
    None_,
    RandomNumber,
    UnixTime
};

enum InValue {
    ZeroIn,
    OneIn,
    TwoIn
};

enum OutValue {
    ZeroOut,
    OneOut,
    TwoOut
};

// Anonymous non-global enum.
// This counts as a class enum, since C++ namespaces
// are represented as classes in Python.
enum {
    AnonymousClassEnum_Value0,
    AnonymousClassEnum_Value1
};

LIBSAMPLE_API OutValue enumInEnumOut(InValue in);

LIBSAMPLE_API Option enumArgumentWithDefaultValue(Option opt = UnixTime);

LIBSAMPLE_API int getNumber(Option opt);

inline double powerOfTwo(double num) {
    return num * num;
}

LIBSAMPLE_API void doSomethingWithArray(const unsigned char *data, unsigned int size,
                                        const char *format = nullptr);

LIBSAMPLE_API int enumItemAsDefaultValueToIntArgument(int value = ZeroIn);

class LIBSAMPLE_API SomeClass
{
public:
    enum class PublicScopedEnum { v1, v2 };

    class SomeInnerClass
    {
    public:
        class OkThisIsRecursiveEnough
        {
        public:
            virtual ~OkThisIsRecursiveEnough() {}
            enum NiceEnum {
                NiceValue1, NiceValue2
            };

            enum class NiceEnumClass {
                NiceClassValue1, NiceClassValue2
            };

            inline int someMethod(SomeInnerClass *) { return 0; }
            virtual OkThisIsRecursiveEnough *someVirtualMethod(OkThisIsRecursiveEnough *arg)
            { return arg; }
        };
    protected:
        enum ProtectedEnum {
            ProtectedItem0,
            ProtectedItem1
        };
    };
    struct SomeOtherInnerClass {
        std::list<SomeInnerClass> someInnerClasses;
    };
protected:
    enum ProtectedEnum {
        ProtectedItem0,
        ProtectedItem1
    };

    PublicScopedEnum protectedMethodReturningPublicScopedEnum() const;
};

LIBSAMPLE_API inline int enumAsInt(SomeClass::PublicScopedEnum value)
{ return static_cast<int>(value); }

class DerivedFromNamespace : public SomeClass::SomeInnerClass::OkThisIsRecursiveEnough
{
public:
    // FIXME Uncomment this when the fix for MSVC is available
    // only to cause namespace confusion
//    enum SampleNamespace {
//    };
    virtual OkThisIsRecursiveEnough *someVirtualMethod(OkThisIsRecursiveEnough *arg) { return arg; }
    inline OkThisIsRecursiveEnough *methodReturningTypeFromParentScope() { return nullptr; }
};

// The combination of the following two overloaded methods could trigger a
// problematic behaviour on the overload decisor, if it isn't working properly.
LIBSAMPLE_API void forceDecisorSideA(ObjectType *object = nullptr);
LIBSAMPLE_API void forceDecisorSideA(const Point &pt, const Str &text,
                                     ObjectType *object = nullptr);

// The combination of the following two overloaded methods could trigger a
// problematic behaviour on the overload decisor, if it isn't working properly.
// This is a variation of forceDecisorSideB.
LIBSAMPLE_API void forceDecisorSideB(int a, ObjectType *object = nullptr);
LIBSAMPLE_API void forceDecisorSideB(int a, const Point &pt, const Str &text,
                                     ObjectType *object = nullptr);

// Add a new signature on type system with only a Point value as parameter.
LIBSAMPLE_API double passReferenceToValueType(const Point &point, double multiplier);
// Add a new signature on type system with only a ObjectType pointer as parameter.
LIBSAMPLE_API int passReferenceToObjectType(const ObjectType &obj, int multiplier);

extern LIBSAMPLE_API int variableInNamespace;

} // namespace SampleNamespace

#endif // SAMPLENAMESPACE_H
