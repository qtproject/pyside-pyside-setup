// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VAL_H
#define VAL_H

#include "libminimalmacros.h"

class LIBMINIMAL_API Val
{
public:
    explicit Val(int valId) : m_valId(valId) {}
    virtual ~Val() {}

    int valId() const { return m_valId; }
    void setValId(int valId) { m_valId = valId; }

    virtual Val passValueType(Val val) { return val; }
    Val callPassValueType(Val val) { return passValueType(val); }

    virtual Val* passValueTypePointer(Val* val) { return val; }
    Val* callPassValueTypePointer(Val* val) { return passValueTypePointer(val); }

    virtual Val* passValueTypeReference(Val& val) { return &val; }
    Val* callPassValueTypeReference(Val& val) { return passValueTypeReference(val); }

    enum ValEnum { One, Other };
    ValEnum oneOrTheOtherEnumValue(ValEnum enumValue) { return enumValue == One ? Other : One; }
private:
    int m_valId;
};

#endif // VAL_H

