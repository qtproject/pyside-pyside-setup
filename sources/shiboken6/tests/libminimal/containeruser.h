// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONTAINERUSER_H
#define CONTAINERUSER_H

#include "libminimalmacros.h"

#include <vector>

/// Exercise simple, sequential containers. More advanced tests are in ListUser
class LIBMINIMAL_API ContainerUser
{
public:
    ContainerUser();
    ~ContainerUser();

    static std::vector<int> createIntVector(int num);
    static int sumIntVector(const std::vector<int> &intVector);

    std::vector<int> &intVector();
    void setIntVector(const  std::vector<int> &);

private:
    std::vector<int> m_intVector;
};

#endif // CONTAINERUSER_H
