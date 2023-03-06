// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "libsamplemacros.h"
#include "oddbool.h"
#include "complex.h"
#include "objecttype.h"

#include <list>
#include <utility>

enum GlobalEnum {
    NoThing,
    FirstThing,
    SecondThing,
    ThirdThing
};

enum GlobalOverloadFuncEnum {
    GlobalOverloadFunc_i,
    GlobalOverloadFunc_d
};

LIBSAMPLE_API void printSomething();
LIBSAMPLE_API int gimmeInt();
LIBSAMPLE_API double gimmeDouble();
LIBSAMPLE_API double multiplyPair(std::pair<double, double> pair);
LIBSAMPLE_API std::list<Complex> gimmeComplexList();
LIBSAMPLE_API Complex sumComplexPair(std::pair<Complex, Complex> cpx_pair);

LIBSAMPLE_API int countCharacters(const char *text);
LIBSAMPLE_API char *makeCString();
LIBSAMPLE_API const char *returnCString();

LIBSAMPLE_API char *returnNullPrimitivePointer();
LIBSAMPLE_API ObjectType *returnNullObjectTypePointer();
LIBSAMPLE_API Event *returnNullValueTypePointer();

// Tests overloading on functions (!methods)
LIBSAMPLE_API GlobalOverloadFuncEnum overloadedFunc(int val);
LIBSAMPLE_API GlobalOverloadFuncEnum overloadedFunc(double val);

LIBSAMPLE_API unsigned int doubleUnsignedInt(unsigned int value);
LIBSAMPLE_API long long doubleLongLong(long long value);
LIBSAMPLE_API unsigned long long doubleUnsignedLongLong(unsigned long long value);
LIBSAMPLE_API short doubleShort(short value);

LIBSAMPLE_API int acceptInt(int x);
LIBSAMPLE_API const int *acceptIntReturnPtr(int x);
LIBSAMPLE_API unsigned int acceptUInt(unsigned int x);
LIBSAMPLE_API long acceptLong(long x);
LIBSAMPLE_API unsigned long acceptULong(unsigned long x);
LIBSAMPLE_API double acceptDouble(double x);

LIBSAMPLE_API int acceptIntReference(int &x);
LIBSAMPLE_API OddBool acceptOddBoolReference(OddBool &x);

LIBSAMPLE_API int sumIntArray(int array[4]);
LIBSAMPLE_API double sumDoubleArray(double array[4]);
LIBSAMPLE_API int sumIntMatrix(int m[2][3]);
LIBSAMPLE_API double sumDoubleMatrix(double m[2][3]);

LIBSAMPLE_API std::string addStdStrings(const std::string &s1, const std::string &s2);
LIBSAMPLE_API std::wstring addStdWStrings(const std::wstring &s1, const std::wstring &s2);

LIBSAMPLE_API void testNullPtrT(std::nullptr_t);

class LIBSAMPLE_API ArrayModifyTest
{
public:
    ArrayModifyTest();
    int sumIntArray(int n, int *array);
};

class LIBSAMPLE_API ClassWithFunctionPointer
{
public:
    explicit ClassWithFunctionPointer();
    void callFunctionPointer(int dummy, void (*fp)(void *));
    static void doNothing(void *operand);
};

#endif // FUNCTIONS_H
