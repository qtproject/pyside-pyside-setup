// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SBKDATE_H
#define SBKDATE_H

#include "libsamplemacros.h"

class LIBSAMPLE_API SbkDate
{
public:
    explicit SbkDate(int d, int m, int y);

    int day() const;
    int month() const;
    int year() const;

private:
    int m_d;
    int m_m;
    int m_y;
};

#endif // SBKDATE_H
