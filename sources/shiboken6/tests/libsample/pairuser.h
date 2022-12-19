// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PAIRUSER_H
#define PAIRUSER_H

#include "libsamplemacros.h"
#include "complex.h"

#include <utility>

class LIBSAMPLE_API PairUser
{
public:
    PairUser() = default;
    virtual ~PairUser() = default;

    virtual std::pair<int, int> createPair();
    std::pair<int, int> callCreatePair();
    static std::pair<Complex, Complex> createComplexPair(Complex cpx0, Complex cpx1);
    double sumPair(std::pair<int, double> pair);

    inline void setPair(std::pair<int, int> pair) { m_pair = pair; }
    inline std::pair<int, int> getPair() { return m_pair; }

private:
    std::pair<int, int> m_pair;
};

#endif // PAIRUSER_H
