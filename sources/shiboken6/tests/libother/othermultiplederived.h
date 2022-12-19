// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OTHERMULTIPLEDERIVED_H
#define OTHERMULTIPLEDERIVED_H

#include "libothermacros.h"
#include "multiple_derived.h"
#include "virtualmethods.h"

class ObjectType;

class LIBOTHER_API OtherMultipleDerived : public MDerived1
{
public:
    // this will use CppCopier from other module (bug#142)
    VirtualMethods returnUselessClass();
    static Base1 *createObject(const std::string &objName);
};

#endif // OTHERMULTIPLEDERIVED_H
