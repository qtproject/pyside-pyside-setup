// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sometime.h"

#include <cstdio>

void Time::setTime()
{
    m_hour = 0;
    m_minute = 0;
    m_second = 0;
    m_msec = 0;
    m_is_null = true;
}

void Time::setTime(int h, int m, int s, int ms)
{
    m_hour = h;
    m_minute = m;
    m_second = s;
    m_msec = ms;
    m_is_null = false;
}

Time::NumArgs Time::somethingCompletelyDifferent()
{
    return ZeroArgs;
}

Time::NumArgs Time::somethingCompletelyDifferent(int, int, ImplicitConv ic, ObjectType *type)
{
    if (type)
        return FourArgs;
    if (ic.ctorEnum() == ImplicitConv::CtorThree && ic.objId() == -1)
        return TwoArgs;
    return ThreeArgs;
}

Str Time::toString() const
{
    if (m_is_null)
        return Str();
    char buffer[13];
    std::snprintf(buffer, sizeof(buffer), "%02d:%02d:%02d.%03d",
                  m_hour, m_minute, m_second, m_msec);
    return Str(buffer);
}

bool Time::operator==(const Time &other) const
{
    return m_hour == other.m_hour
            && m_minute == other.m_minute
            && m_second == other.m_second
            && m_msec == other.m_msec
            && m_is_null == other.m_is_null;
}

bool Time::operator!=(const Time &other) const
{
    return !operator==(other);
}

Time::operator Str() const
{
    return Time::toString();
}
