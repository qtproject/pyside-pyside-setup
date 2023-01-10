// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "containeruser.h"

#include <algorithm>
#include <numeric>

ContainerUser::ContainerUser() : m_intVector{1, 2, 3}, m_intArray{1, 2, 3}
{
}

ContainerUser::~ContainerUser() = default;

std::vector<int> ContainerUser::createIntVector(int num)
{
    std::vector<int> retval(num);
    std::iota(retval.begin(), retval.end(), 0);
    return retval;
}

int ContainerUser::sumIntVector(const std::vector<int> &intVector)
{
    return std::accumulate(intVector.cbegin(), intVector.cend(), 0);
}

std::vector<int> &ContainerUser::intVector()
{
    return m_intVector;
}

void ContainerUser::setIntVector(const std::vector<int> &v)
{
    m_intVector = v;
}

std::array<int, 3> ContainerUser::createIntArray()
{
    return {1, 2, 3};
}

int ContainerUser::sumIntArray(const std::array<int, 3> &intArray)
{
    return std::accumulate(intArray.cbegin(), intArray.cend(), 0);
}

std::array<int, 3> &ContainerUser::intArray()
{
    return m_intArray;
}

void ContainerUser::setIntArray(const std::array<int, 3> &a)
{
    m_intArray = a;
}
