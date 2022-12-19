// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MINBOOL_H
#define MINBOOL_H

#include "libminimalmacros.h"

class LIBMINIMAL_API MinBool
{
public:
    inline explicit MinBool(bool b) : m_value(b) {}
    bool value() const { return m_value; }
    inline MinBool operator!() const { return MinBool(!m_value); }
    inline MinBool& operator|=(const MinBool& other) {
        m_value = m_value | other.m_value;
        return *this;
    }

private:
    bool m_value;
};

inline bool operator==(MinBool b1, bool b2) { return (!b1).value() == !b2; }
inline bool operator==(bool b1, MinBool b2) { return (!b1) == (!b2).value(); }
inline bool operator==(MinBool b1, MinBool b2) { return (!b1).value() == (!b2).value(); }
inline bool operator!=(MinBool b1, bool b2) { return (!b1).value() != !b2; }
inline bool operator!=(bool b1, MinBool b2) { return (!b1) != (!b2).value(); }
inline bool operator!=(MinBool b1, MinBool b2) { return (!b1).value() != (!b2).value(); }

class LIBMINIMAL_API MinBoolUser
{
public:
    MinBoolUser() : m_minbool(MinBool(false)) {}
    virtual ~MinBoolUser() = default;
    inline MinBool minBool() { return m_minbool; }
    inline void setMinBool(MinBool minBool) { m_minbool = minBool; }
    virtual MinBool invertedMinBool() { return !m_minbool; }
    inline MinBool callInvertedMinBool() { return invertedMinBool(); }

private:
    MinBool m_minbool;
};

#endif
