// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ODDBOOL_H
#define ODDBOOL_H

#include "libsamplemacros.h"

#include <type_traits>

#if __cplusplus >= 202002 || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002)
#  include <compare>
#endif

class OddBool
{

public:
    inline explicit OddBool(bool b) : m_value(b) {}
    bool value() const { return m_value; }

    inline OddBool operator!() const { return OddBool(!m_value); }

private:
    bool m_value;
};

inline bool operator==(OddBool b1, bool b2) { return (!b1).value() == !b2; }
inline bool operator==(bool b1, OddBool b2) { return (!b1) == (!b2).value(); }
inline bool operator==(OddBool b1, OddBool b2) { return (!b1).value() == (!b2).value(); }
inline bool operator!=(OddBool b1, bool b2) { return (!b1).value() != !b2; }
inline bool operator!=(bool b1, OddBool b2) { return (!b1) != (!b2).value(); }
inline bool operator!=(OddBool b1, OddBool b2) { return (!b1).value() != (!b2).value(); }

class OddBoolUser
{
public:
    OddBoolUser() : m_oddbool(OddBool(false)) {}
    OddBoolUser(const OddBool &oddBool) : m_oddbool(oddBool) {}
    virtual ~OddBoolUser() {}

    inline OddBool oddBool() { return m_oddbool; }
    inline void setOddBool(OddBool oddBool) { m_oddbool = oddBool; }

    virtual OddBool invertedOddBool()
    {
        return !m_oddbool;
    }

    inline OddBool callInvertedOddBool()
    {
        return invertedOddBool();
    }

    static inline OddBool getOddBool(const OddBoolUser &oddBoolUser)
    {
        return oddBoolUser.m_oddbool;
    }

private:
    OddBool m_oddbool;
};

class LIBSAMPLE_API ComparisonTester
{
public:
    explicit ComparisonTester(int v);
    ComparisonTester &operator=(int v);

    int compare(const ComparisonTester &rhs) const;

private:
    int m_value;
};

// Hide the comparison operators from the clang parser (see typesystem_sample.xml:184,
// oddbool_test.py)

inline std::enable_if<std::is_assignable<ComparisonTester, int>::value, bool>::type
    operator==(const ComparisonTester &c1, const ComparisonTester &c2)
{ return c1.compare(c2) == 0; }

inline std::enable_if<std::is_assignable<ComparisonTester, int>::value, bool>::type
    operator!=(const ComparisonTester &c1, const ComparisonTester &c2)
{ return c1.compare(c2) != 0; }

class LIBSAMPLE_API SpaceshipComparisonTester
{
public:
    explicit SpaceshipComparisonTester(int v);

#if __cplusplus >= 202002 || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002)
    auto operator<=>(const SpaceshipComparisonTester &rhs) const = default;

    enum Enabled { HasSpaceshipOperator = 1 };
#else
    enum Enabled { HasSpaceshipOperator = 0 };
#endif // C++ 20

private:
    int m_value;
};

#endif // ODDBOOL_H
