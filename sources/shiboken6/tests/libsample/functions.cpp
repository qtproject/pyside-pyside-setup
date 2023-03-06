// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "functions.h"

#include <cstring>
#include <algorithm>
#include <iostream>
#include <numeric>

void printSomething()
{
    std::cout << __FUNCTION__ << std::endl;
}

int gimmeInt()
{
    static int val = 2;
    val = val * 1.3;
    return val;
}

double gimmeDouble()
{
    static double val = 7.77;
    val = val * 1.3;
    return val;
}

std::list<Complex> gimmeComplexList()
{
    std::list<Complex> lst;
    lst.push_back(Complex());
    lst.push_back(Complex(1.1, 2.2));
    lst.push_back(Complex(1.3, 2.4));
    return lst;
}

Complex sumComplexPair(std::pair<Complex, Complex> cpx_pair)
{
    return cpx_pair.first + cpx_pair.second;
}

double multiplyPair(std::pair<double, double> pair)
{
    return pair.first * pair.second;
}

int countCharacters(const char *text)
{
    if (!text)
        return -1;
    return std::strlen(text);
}

char *makeCString()
{
    char *string = new char[strlen(__FUNCTION__) + 1];
    std::strcpy(string, __FUNCTION__);
    return string;
}

const char *returnCString()
{
    return __FUNCTION__;
}

GlobalOverloadFuncEnum overloadedFunc(int)
{
    return GlobalOverloadFunc_i;
}

GlobalOverloadFuncEnum overloadedFunc(double)
{
    return GlobalOverloadFunc_d;
}

char *returnNullPrimitivePointer()
{
    return nullptr;
}

ObjectType *returnNullObjectTypePointer()
{
    return nullptr;
}

Event *returnNullValueTypePointer()
{
    return nullptr;
}

unsigned int doubleUnsignedInt(unsigned int value)
{
    return value * 2;
}

long long doubleLongLong(long long value)
{
    return value * 2;
}

unsigned long long doubleUnsignedLongLong(unsigned long long value)
{
    return value * 2;
}

short doubleShort(short value)
{
    return value * 2;
}

int acceptInt(int x)
{
    return x;
}

const int *acceptIntReturnPtr(int x)
{
    return new int(x);
}

unsigned int acceptUInt(unsigned int x)
{
    return x;
}

long acceptLong(long x)
{
    return x;
}

unsigned long acceptULong(unsigned long x)
{
    return x;
}

double acceptDouble(double x)
{
    return x;
}

int acceptIntReference(int &x)
{
    return x;
}

OddBool acceptOddBoolReference(OddBool &x)
{
    return x;
}

int sumIntArray(int array[4])
{
    return std::accumulate(array, array + 4, 0);
}

double sumDoubleArray(double array[4])
{
    return std::accumulate(array, array + 4, double(0));
}

int sumIntMatrix(int m[2][3])
{
    int result = 0;
    for (int r = 0; r < 2; ++r) {
        for (int c = 0; c < 3; ++c)
            result += m[r][c];
    }
    return result;
}

double sumDoubleMatrix(double m[2][3])
{
    double result = 0;
    for (int r = 0; r < 2; ++r) {
        for (int c = 0; c < 3; ++c)
            result += m[r][c];
    }
    return result;
}

ArrayModifyTest::ArrayModifyTest()
{
}

int ArrayModifyTest::sumIntArray(int n, int *array)
{
   return std::accumulate(array, array + n, 0);
}

ClassWithFunctionPointer::ClassWithFunctionPointer()
{
    callFunctionPointer(0, &ClassWithFunctionPointer::doNothing);
}

void ClassWithFunctionPointer::callFunctionPointer(int dummy, void (*fp)(void *))
{
    size_t a = dummy;
    fp(reinterpret_cast<void *>(a));
}

void ClassWithFunctionPointer::doNothing(void *operand)
{
    (void) operand;
}

std::string addStdStrings(const std::string &s1, const std::string &s2)
{
    return s1 + s2;
}

std::wstring addStdWStrings(const std::wstring &s1, const std::wstring &s2)
{
    return s1 + s2;
}

void testNullPtrT(std::nullptr_t)
{
    std::cout << __FUNCTION__ << '\n';
}
