// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMART_INTEGER_H
#define SMART_INTEGER_H

#include "libsmartmacros.h"

class LIB_SMART_API Integer {
public:
    Integer();
    Integer(const Integer &other);
    Integer &operator=(const Integer &other);
    ~Integer();
    void printInteger() const;

    int value() const;
    void setValue(int v);

    int compare(const Integer &rhs) const;

    int m_int; // public for testing member field access.
};

inline bool operator==(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) == 0;
}

inline bool operator!=(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) != 0;
}

inline bool operator<(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) < 0;
}

inline bool operator<=(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) <= 0;
}

inline bool operator>(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) > 0;
}

inline bool operator>=(const Integer &lhs, const Integer &rhs)
{
    return lhs.compare(rhs) >= 0;
}

namespace Smart {
class LIB_SMART_API Integer2 : public Integer {
public:
    Integer2();
    Integer2(const Integer2 &);
    Integer2 &operator=(const Integer2 &);
};
} // namespace Smart

#endif // SMART_INTEGER_H
