// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SOMETIME_H
#define SOMETIME_H

#include "libsamplemacros.h"
#include "str.h"
#include "implicitconv.h"
#include "objecttype.h"

class LIBSAMPLE_API Time
{
public:
    enum NumArgs {
        ZeroArgs,
        TwoArgs,
        ThreeArgs,
        FourArgs
    };

    Time() = default;
    explicit Time(int h, int m, int s = 0, int ms = 0) :
        m_hour(h), m_minute(m), m_second(s), m_msec(ms), m_is_null(false)
    {}

    ~Time() = default;

    inline bool isNull() const { return m_is_null; }

    inline int hour() const { return m_hour; }
    inline int minute() const { return m_minute; }
    inline int second() const { return m_second; }
    inline int msec() const { return m_msec; }

    void setTime();
    void setTime(int h, int m, int s = 0, int ms = 0);

    // This one is completely different from the other methods in this class,
    // it was added to give the overload decisor a really hard time with
    // an value-type with implicit conversion and a default argument, and also
    // an object-type, just because I feel like it.
    NumArgs somethingCompletelyDifferent();
    NumArgs somethingCompletelyDifferent(int h, int m,
                                         ImplicitConv ic = ImplicitConv::CtorThree,
                                         ObjectType *type = nullptr);

    Str toString() const;
    bool operator==(const Time &other) const;
    bool operator!=(const Time &other) const;

    // This cast operator must become an implicit conversion of Str.
    operator Str() const;

private:
    int m_hour = 0;
    int m_minute = 0;
    int m_second = 0;
    int m_msec = 0;

    bool m_is_null = true;
};

#endif // SOMETIME_H
