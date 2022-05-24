// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sbkdate.h"

SbkDate::SbkDate(int d, int m, int y) : m_d(d), m_m(m), m_y(y)
{
}

int SbkDate::day() const
{
    return m_d;
}

int SbkDate::month() const
{
    return m_m;
}

int SbkDate::year() const
{
    return m_y;
}
