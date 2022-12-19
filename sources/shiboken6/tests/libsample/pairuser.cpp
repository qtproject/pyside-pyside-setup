// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "pairuser.h"

std::pair<int, int> PairUser::callCreatePair()
{
    return createPair();
}

std::pair<int, int> PairUser::createPair()
{
    return {10, 20};
}

std::pair<Complex, Complex> PairUser::createComplexPair(Complex cpx0, Complex cpx1)
{
    return {cpx0, cpx1};
}

double PairUser::sumPair(std::pair<int, double> pair)
{
    return ((double) pair.first) + pair.second;
}
