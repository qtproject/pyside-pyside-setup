// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#include "intwrapper.h"

int IntWrapper::toInt() const
{
    return m_number;
}

IntWrapper &IntWrapper::operator ++()
{
    ++m_number;
    return *this;
}

IntWrapper IntWrapper::operator++(int)
{
    IntWrapper result(*this);
    ++m_number;
    return result;
}

IntWrapper &IntWrapper::operator--()
{
    --m_number;
    return *this;
}

IntWrapper IntWrapper::operator--(int)
{
    IntWrapper result(*this);
    --m_number;
    return result;
}
