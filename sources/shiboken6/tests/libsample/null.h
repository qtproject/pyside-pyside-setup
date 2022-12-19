// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef NULL_H
#define NULL_H

class Null
{
public:
    Null(bool value) : m_isNull(value) {}
    Null() = default;

    void setIsNull(bool flag) { m_isNull = flag; }

private:
    bool m_isNull = false;
};

#endif // NULL_H
