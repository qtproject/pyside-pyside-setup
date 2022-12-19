// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "othermultiplederived.h"

VirtualMethods OtherMultipleDerived::returnUselessClass()
{
    return VirtualMethods();
}

Base1 *OtherMultipleDerived::createObject(const std::string &objName)
{
    if (objName == "Base1")
        return new Base1;
    if (objName == "MDerived1")
        return new MDerived1;
    if (objName == "SonOfMDerived1")
        return new SonOfMDerived1;
    if (objName == "MDerived3")
        return new MDerived3;
    if (objName == "OtherMultipleDerived")
        return new OtherMultipleDerived;
    return nullptr;
}
